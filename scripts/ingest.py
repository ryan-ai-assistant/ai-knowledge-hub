import os, re, json, hashlib, pathlib, shutil, yaml, difflib, subprocess
from datetime import datetime

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONFIG = yaml.safe_load((ROOT / "taxonomy_config.yaml").read_text(encoding="utf-8"))

INBOX = ROOT / CONFIG["paths"]["inbox"]
PROMPTS_DIR = ROOT / CONFIG["paths"]["prompts"]
TEMPLATES_DIR = ROOT / CONFIG["paths"]["templates"]
FRAMEWORKS_DIR = ROOT / CONFIG["paths"]["frameworks"]
REPORT_PATH = ROOT / CONFIG["paths"]["catalog_report"]
PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
FRAMEWORKS_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

BANNED = CONFIG["style_bans"]["banned_phrases"]
BAN_EDASH = CONFIG["style_bans"]["em_dashes"]
BAN_EMOJI = CONFIG["style_bans"]["emojis"]

CONVERTIBLE_EXTS = {".md",".txt",".rtf",".html",".json",".yaml",".yml",".docx"}
SKIP_EXTS = {".pdf",".png",".jpg",".jpeg",".gif",".svg",".pptx",".xlsx",".csv",".mp3",".mp4",".mov",".zip",".gz",".tar",".rar"}

def read_text(p: pathlib.Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except:
        return p.read_text(errors="ignore")

def convert_to_markdown(path: pathlib.Path, text: str) -> str:
    ext = path.suffix.lower()
    if ext == ".md":
        return text
    if ext not in CONVERTIBLE_EXTS:
        return text
    fmt = ext.strip(".")
    try:
        proc = subprocess.run(["pandoc", "-f", fmt, "-t", "gfm"], input=text.encode("utf-8"), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if proc.returncode == 0:
            return proc.stdout.decode("utf-8")
        return text
    except Exception:
        return text

def split_front_matter(txt: str):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", txt, re.DOTALL)
    if m:
        return m.group(1), m.group(2)
    return None, txt

def parse_yaml(yml: str) -> dict:
    try:
        return yaml.safe_load(yml) or {}
    except:
        return {}

def slugify(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"-+", "-", s)
    return s[:80]

def synthesize_front_matter(body: str, path: pathlib.Path) -> dict:
    title = None
    ht = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
    if ht: title = ht.group(1).strip()
    if not title: title = path.stem.replace("-", " ").title()
    slug = slugify(title)
    return {
        "title": title,
        "slug": slug,
        "tags": [],
        "audience": CONFIG["defaults"]["audience"],
        "task_type": "unspecified",
        "model": CONFIG["defaults"]["model"],
        "version": "1.0",
        "owner": CONFIG["defaults"]["owner"],
    }

def normalize_tags(tags):
    tags = [t.strip() for t in (tags or []) if t]
    mapped = set()
    syn = CONFIG.get("tag_synonyms", {})
    for t in tags:
        tl = t.lower()
        mapped.add(tl)
        for canonical, alts in syn.items():
            if tl == canonical or tl in [a.lower() for a in alts]:
                mapped.add(canonical)
    return sorted(mapped)

def classify_destination(tags):
    tset = set(tags)
    if any(t.startswith("frameworks/") for t in tset):
        return FRAMEWORKS_DIR
    if any(t.startswith("templates/") for t in tset):
        return TEMPLATES_DIR
    return PROMPTS_DIR

def content_fingerprint(text: str) -> str:
    yml, body = split_front_matter(text)
    base = body if body else text
    base = re.sub(r"\s+", " ", base).strip().lower()
    return hashlib.sha256(base.encode("utf-8")).hexdigest()

def nearest_match(candidate_text: str, existing_texts: list):
    best = (0.0, None)
    for path, txt in existing_texts:
        r = difflib.SequenceMatcher(None, candidate_text, txt).ratio()
        if r > best[0]:
            best = (r, path)
    return best

def enforce_style(body: str) -> str:
    if BAN_EMOJI:
        body = re.sub(r"[\U0001F300-\U0001FAFF\U00002700-\U000027BF]+", "", body)
    if BAN_EDASH:
        body = body.replace("—", ",")
    for phrase in BANNED:
        body = re.sub(re.escape(phrase), "", body, flags=re.IGNORECASE)
    return body

def ensure_modules(fm: dict, dest_dir: pathlib.Path):
    modules = fm.get("modules", []) or []
    defaults = []
    if dest_dir == PROMPTS_DIR:
        defaults = CONFIG["defaults"]["modules"]["prompts"]
    elif dest_dir == TEMPLATES_DIR:
        defaults = CONFIG["defaults"]["modules"]["templates"]
    elif dest_dir == FRAMEWORKS_DIR:
        defaults = CONFIG["defaults"]["modules"]["frameworks"]
    for m in defaults:
        if m not in modules:
            modules.append(m)
    fm["modules"] = modules
    return fm

def write_normalized(dest_dir, fm, body):
    slug = fm.get("slug") or slugify(fm.get("title","item"))
    sub = "general"
    for t in fm.get("tags", []):
        if "/" in t and not t.startswith("templates/") and not t.startswith("frameworks/"):
            sub = t
            break
    if dest_dir == TEMPLATES_DIR:
        out = dest_dir / f"{slug}.md"
    elif dest_dir == FRAMEWORKS_DIR:
        out = dest_dir / f"{slug}.md"
    else:
        out = dest_dir / sub / f"{slug}.md"
        out.parent.mkdir(parents=True, exist_ok=True)
    fm["slug"] = slug
    txt = "---\n" + yaml.safe_dump(fm, sort_keys=False).strip() + "\n---\n\n" + body.strip() + "\n"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(txt, encoding="utf-8")
    return out

def load_existing_texts():
    existing = []
    for p in ROOT.rglob("*.md"):
        if str(p).startswith(str(INBOX)) or ".github" in str(p) or "catalog" in str(p):
            continue
        existing.append((p, p.read_text(encoding="utf-8")))
    return existing

def main():
    report = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "added": [],
        "duplicates": [],
        "skipped": [],
        "errors": []
    }
    existing_texts = load_existing_texts()

    if not INBOX.exists():
        REPORT_PATH.write_text("# Ingest Report\n\n_No inbox folder found._\n", encoding="utf-8")
        return

    for p in INBOX.rglob("*"):
        if p.is_dir():
            continue
        if p.suffix.lower() in SKIP_EXTS:
            report["skipped"].append({"inbox": str(p), "reason": f"binary or unsupported ({p.suffix})"})
            continue

        raw = read_text(p)
        raw = convert_to_markdown(p, raw)

        fm_txt, body = split_front_matter(raw)
        fm = parse_yaml(fm_txt) if fm_txt else synthesize_front_matter(body, p)

        fm["tags"] = normalize_tags(fm.get("tags", []))

        fm.setdefault("audience", CONFIG["defaults"]["audience"])
        fm.setdefault("task_type", fm.get("task_type", "unspecified"))
        fm.setdefault("model", CONFIG["defaults"]["model"])
        fm.setdefault("version", fm.get("version", "1.0"))
        fm.setdefault("owner", CONFIG["defaults"]["owner"])

        body = enforce_style(body)

        dest_dir = classify_destination(fm["tags"])
        fm = ensure_modules(fm, dest_dir)

        cand_fp = content_fingerprint(raw)
        exact_hit = None
        for path, txt in existing_texts:
            if content_fingerprint(txt) == cand_fp:
                exact_hit = path
                break
        if exact_hit:
            report["duplicates"].append({"inbox": str(p), "existing": str(exact_hit), "type": "exact"})
            continue

        ratio, near = nearest_match(raw, existing_texts)
        if ratio >= 0.92:
            report["duplicates"].append({"inbox": str(p), "existing": str(near), "type": f"near:{ratio:.3f}"})
            continue

        out = write_normalized(dest_dir, fm, body)
        report["added"].append({"inbox": str(p), "added_as": str(out)})
        existing_texts.append((out, out.read_text(encoding="utf-8")))

    lines = ["# Ingest Report", "", f"_Generated: {report['timestamp']}_", ""]
    if report["added"]:
        lines += ["## Added", ""] + [f"- {a['inbox']} → **{a['added_as']}**" for a in report["added"]] + [""]
    if report["duplicates"]:
        lines += ["## Duplicates/Skipped", ""] + [f"- {d['inbox']} ≈ {d['existing']} ({d['type']})" for d in report["duplicates"]] + [""]
    if report["skipped"]:
        lines += ["## Skipped", ""] + [f"- {s['inbox']}: {s['reason']}" for s in report["skipped"]] + [""]
    if report["errors"]:
        lines += ["## Errors", ""] + [f"- {e['inbox']}: {e['error']}" for e in report["errors"]] + [""]
    if not (report["added"] or report["duplicates"] or report["errors"] or report["skipped"]):
        lines.append("_No changes._")
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()
