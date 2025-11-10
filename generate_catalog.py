import os, re, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
CATALOG = ROOT / "catalog"
CATALOG.mkdir(exist_ok=True, parents=True)

def parse_front_matter(text):
    m = re.match(r'^---\n(.*?)\n---\n', text, re.DOTALL)
    data = {}
    if m:
        block = m.group(1)
        for line in block.splitlines():
            if not line.strip() or line.strip().startswith("#"): 
                continue
            if ":" in line:
                k, v = line.split(":", 1)
                data[k.strip()] = v.strip()
    return data

rows = []
for path in ROOT.rglob("*.md"):
    if any(p in path.parts for p in [".github", "catalog"]):
        continue
    rel = path.relative_to(ROOT).as_posix()
    with open(path, "r", encoding="utf-8") as f:
        txt = f.read()
    fm = parse_front_matter(txt)
    title = fm.get("title", "")
    tags_line = fm.get("tags", "").strip("[]")
    tags = [t.strip() for t in tags_line.split(",")] if tags_line else []
    owner = fm.get("owner", "")
    slug = fm.get("slug", path.stem)
    rows.append({"title": title, "slug": slug, "path": rel, "tags": tags, "owner": owner})

with open(CATALOG / "index.json", "w", encoding="utf-8") as f:
    json.dump(rows, f, indent=2)

# Update README catalog table
readme_path = ROOT / "README.md"
with open(readme_path, "r", encoding="utf-8") as f:
    readme = f.read()

table_header = "| Title | Slug | Path | Tags |\n|---|---|---|---|\n"
table_rows = []
for r in sorted(rows, key=lambda x: x["title"].lower()):
    tags_str = ", ".join([t for t in r["tags"] if t])
    table_rows.append(f"| {r['title']} | {r['slug']} | {r['path']} | {tags_str} |")
table = table_header + "\n".join(table_rows) if table_rows else "*No items yet.*"

start = "<!-- CATALOG_TABLE_START -->"
end = "<!-- CATALOG_TABLE_END -->"
new_readme = re.sub(f"{start}.*?{end}", f"{start}\n{table}\n{end}", readme, flags=re.S)

with open(readme_path, "w", encoding="utf-8") as f:
    f.write(new_readme)
