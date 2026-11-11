#!/usr/bin/env python3
"""Rebuild the writeups index from each file's front matter.

Outputs (all generated, do not edit by hand):
  - README.md            -> blocks between <!-- STATS --> and <!-- INDEX --> markers
  - <category>/README.md -> per-category listing
  - index.json           -> machine-readable index consumed by the profile README

To add a writeup: drop a .md file (copied from TEMPLATE.md) into a category folder.
"""
import json
import pathlib
import re
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent
REPO_BLOB = "https://github.com/damnz-dev/writeups/blob/main"

# folder -> (display name, accent color)
CATEGORIES = {
    "machines":  ("Machines",  "5eead4"),
    "web":       ("Web",       "38bdf8"),
    "pwn":       ("Pwn",       "f87171"),
    "crypto":    ("Crypto",    "a78bfa"),
    "rev":       ("Reversing", "fbbf24"),
    "forensics": ("Forensics", "34d399"),
    "misc":      ("Misc",      "94a3b8"),
}
DIFFICULTY = {"easy": "22c55e", "medium": "f59e0b", "hard": "ef4444", "insane": "a855f7"}
BG = "0b1117"


def esc(text: str) -> str:
    """Escape a string for a shields.io static badge path segment."""
    return urllib.parse.quote(str(text).replace("-", "--").replace("_", "__").replace(" ", "_"))


def badge(message: str, color: str, label: str | None = None, style: str = "flat-square") -> str:
    path = f"{esc(label)}-{esc(message)}-{color}" if label else f"{esc(message)}-{color}"
    return f"https://img.shields.io/badge/{path}?style={style}&labelColor={BG}"


def parse_front_matter(text: str) -> dict:
    match = re.match(r"^\ufeff?---\s*\r?\n(.*?)\r?\n---\s*\r?\n", text, re.S)
    if not match:
        return {}
    data = {}
    for line in match.group(1).splitlines():
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            value = [v.strip().strip("'\"") for v in value[1:-1].split(",") if v.strip()]
        else:
            value = value.strip("'\"")
        data[key.strip()] = value
    return data


def collect() -> list[dict]:
    entries = []
    for folder in CATEGORIES:
        for path in sorted((ROOT / folder).glob("*.md")):
            if path.name.lower() == "readme.md":
                continue
            fm = parse_front_matter(path.read_text(encoding="utf-8"))
            tags = fm.get("tags", [])
            entries.append({
                "title": fm.get("title") or path.stem.replace("-", " ").title(),
                "subtitle": fm.get("subtitle", ""),
                "category": folder,
                "difficulty": (fm.get("difficulty") or "unrated").lower(),
                "tags": tags if isinstance(tags, list) else [tags],
                "date": fm.get("date", ""),
                "path": f"{folder}/{path.name}",
                "url": f"{REPO_BLOB}/{folder}/{path.name}",
            })
    entries.sort(key=lambda e: (e["date"], e["title"].lower()))
    for i, e in enumerate(entries, 1):
        e["id"] = f"{i:02d}"
    return entries


def row(e: dict, rel_prefix: str = "./") -> str:
    name, color = CATEGORIES[e["category"]]
    diff = e["difficulty"]
    title = f"**{e['title']}**" + (f"<br><sub>{e['subtitle']}</sub>" if e["subtitle"] else "")
    tags = " ".join(f"`{t}`" for t in e["tags"]) or "—"
    return (
        f"| `{e['id']}` | {title} "
        f"| <img src=\"{badge(name, color)}\" alt=\"{name}\"/> "
        f"| <img src=\"{badge(diff.title(), DIFFICULTY.get(diff, '475569'))}\" alt=\"{diff}\"/> "
        f"| {tags} "
        f"| [`↗ read`]({rel_prefix}{e['path']}) |"
    )


TABLE_HEAD = "| # | Case | Category | Difficulty | Tags | Link |\n|:-:|:-----|:--------:|:----------:|:-----|:----:|"


def replace_block(text: str, marker: str, content: str) -> str:
    pattern = re.compile(rf"(<!-- {marker}:START -->).*?(<!-- {marker}:END -->)", re.S)
    return pattern.sub(lambda m: f"{m.group(1)}\n{content}\n{m.group(2)}", text)


def main() -> None:
    entries = collect()

    # README: stats badges
    counts = {c: sum(e["category"] == c for e in entries) for c in CATEGORIES}
    stats = [f'<img src="{badge(str(len(entries)), "5eead4", "case files", "for-the-badge")}" alt="total"/>']
    stats += [
        f'<img src="{badge(str(n), color, name)}" alt="{name}"/>'
        for c, (name, color) in CATEGORIES.items() if (n := counts[c])
    ]
    stats_block = '<p align="center">\n  ' + "\n  ".join(stats) + "\n</p>"

    rows = "\n".join(row(e) for e in reversed(entries)) or "| — | _No writeups yet_ | | | | |"
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    text = replace_block(text, "STATS", stats_block)
    text = replace_block(text, "INDEX", f"{TABLE_HEAD}\n{rows}")
    readme.write_text(text, encoding="utf-8")

    # Per-category READMEs
    for folder, (name, color) in CATEGORIES.items():
        items = [e for e in reversed(entries) if e["category"] == folder]
        body = "\n".join(row(e, "../") for e in items) if items else "| — | _No writeups yet_ | | | | |"
        (ROOT / folder / "README.md").write_text(
            f'# <img src="{badge(name, color, style="for-the-badge")}" alt="{name}"/>\n\n'
            f"{TABLE_HEAD}\n{body}\n\n<sub>← back to the [full index](../README.md)</sub>\n",
            encoding="utf-8",
        )

    # Machine-readable index for the profile README
    (ROOT / "index.json").write_text(
        json.dumps({"total": len(entries), "counts": counts, "entries": entries}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"indexed {len(entries)} writeup(s)")


if __name__ == "__main__":
    main()
