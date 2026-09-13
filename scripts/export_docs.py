#!/usr/bin/env python3
"""Export Genius AI (space G) Confluence pages to hire/docs as markdown."""

from __future__ import annotations

import json
import re
import subprocess
import time
from pathlib import Path

HIRE = Path("/home/havok/Work/lunaya/genai/hire")
DOCS = HIRE / "docs"
TREE = Path("/tmp/space-g-tree.json")
EXPORTABLE = Path("/tmp/space-g-exportable.json")


def slug(title: str) -> str:
    s = title.lower()
    for ch in ("—", "–", "−", "&"):
        s = s.replace(ch, " ")
    s = re.sub(r"[^\w\s\-]+", "", s, flags=re.UNICODE)
    s = re.sub(r"[\s_\-]+", "-", s.strip()).strip("-")
    return (s[:90] or "page").rstrip("-")


def path_for(pid: str, by_id: dict) -> Path:
    """Skip the space home page as a directory prefix; use it as index.md."""
    chain = []
    cur = by_id.get(pid)
    while cur is not None:
        chain.append(cur)
        parent = cur.get("parentId")
        cur = by_id.get(str(parent)) if parent else None
    chain.reverse()
    # Root home → index.md
    if len(chain) == 1:
        return Path("index.md")
    # Drop home from directory prefix
    if chain[0].get("title", "").lower().startswith("genai home"):
        chain = chain[1:]
    *dirs, leaf = chain
    parts = [slug(x["title"]) for x in dirs]
    filename = f"{slug(leaf['title'])}.md"
    return Path(*parts) / filename if parts else Path(filename)


def twg_body(page_id: str) -> str:
    out = Path(f"/tmp/hire-md-{page_id}.md")
    cmd = [
        "twg",
        "confluence",
        "content",
        "get",
        page_id,
        "--detail",
        "full",
        "--format",
        "markdown",
        "--body-only",
        "--output-file",
        str(out),
    ]
    for attempt in range(4):
        p = subprocess.run(cmd, capture_output=True, text=True)
        if p.returncode == 0 and out.exists():
            text = out.read_text(encoding="utf-8")
            if text.strip():
                return text
            # Empty body can be valid (e.g. graph/embed-heavy pages)
            if attempt == 3:
                return (
                    "_This Confluence page has no markdown body "
                    "(likely an embed, whiteboard, or media-heavy page). "
                    "Open the source URL for the interactive content._\n"
                )
        time.sleep(1 + attempt)
    raise RuntimeError(
        f"failed to fetch {page_id}: {(p.stderr or p.stdout)[-500:]}"
    )


def main() -> None:
    if not TREE.exists() or not EXPORTABLE.exists():
        raise SystemExit("missing /tmp/space-g-tree.json or exportable list; re-run tree first")

    tree = json.loads(TREE.read_text())
    root = tree["data"]["root"]
    descendants = tree["data"]["descendants"]
    by_id = {str(root["id"]): {**root, "depth": 0, "parentId": None}}
    for d in descendants:
        by_id[str(d["id"])] = d

    pages = [
        p
        for p in json.loads(EXPORTABLE.read_text())
        if p.get("type") in ("page", "live_doc", "blogpost", None)
    ]

    # Build path from Confluence hierarchy
    def path_for_page(pid: str) -> Path:
        return path_for(pid, by_id)

    # Fresh docs tree
    if DOCS.exists():
        import shutil

        shutil.rmtree(DOCS)
    DOCS.mkdir(parents=True, exist_ok=True)
    index_rows = []
    errors = []

    for i, p in enumerate(pages, 1):
        pid = str(p["id"])
        title = p["title"]
        rel = path_for_page(pid)
        dest = DOCS / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        print(f"[{i}/{len(pages)}] {title} → {rel}", flush=True)
        try:
            body = twg_body(pid).strip() + "\n"
        except Exception as e:
            errors.append((pid, title, str(e)))
            print(f"  ERR {e}", flush=True)
            continue

        url = f"https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/{pid}"
        header = (
            f"# {title}\n\n"
            f"> Source: [{url}]({url})  \n"
            f"> Confluence page id `{pid}` (exported for Genius AI hiring take-home).\n\n"
            f"---\n\n"
        )
        # Avoid double H1 if body already starts with the title
        body_out = body
        first_line = body.splitlines()[0].strip() if body else ""
        if first_line.lstrip("# ").strip() == title:
            body_out = "\n".join(body.splitlines()[1:]).lstrip() + "\n"

        dest.write_text(header + body_out, encoding="utf-8")
        index_rows.append(
            {
                "id": pid,
                "title": title,
                "path": str(rel).replace("\\", "/"),
                "depth": p.get("depth", 0),
                "parentId": p.get("parentId"),
            }
        )

    # README
    lines = [
        "# Genius AI — frontend take-home briefing pack",
        "",
        "This directory mirrors our **Confluence space G (Genius AI)** docs as markdown,",
        "exported for take-home assignments so candidates work from the **real product context**",
        "instead of toy puzzles.",
        "",
        "## How to use",
        "",
        "1. Start at [`docs/index.md`](docs/index.md) (GenAI Home), then Architecture and Design, then the goal/design pages that match the assignment brief.",
        "2. Workflow **Action:** pages under `docs/architecture-and-design-genai-lunaya-flow/workflow-actions-reference/` are API/reference detail — skim unless the brief points you there.",
        "3. Treat links to `geniusaidubai.atlassian.net` as the canonical source; this pack may lag slightly.",
        "",
        "Markdown was exported from Confluence (same pages as the PDF pack under `../docs/confluence-pdfs/`) for readable take-home material.",
        "",
        "## Contents",
        "",
    ]
    for row in index_rows:
        indent = "  " * int(row["depth"])
        lines.append(f"{indent}- [{row['title']}](docs/{row['path']})")
    lines += [
        "",
        f"## Export stats",
        "",
        f"- Pages written: **{len(index_rows)}**",
        f"- Failures: **{len(errors)}**",
        "",
    ]
    if errors:
        lines.append("### Failures")
        lines.append("")
        for pid, title, err in errors:
            lines.append(f"- `{pid}` {title}: {err}")
        lines.append("")

    (HIRE / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (HIRE / "docs" / "manifest.json").write_text(
        json.dumps({"pages": index_rows, "errors": errors}, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {len(index_rows)} pages, {len(errors)} errors → {HIRE}", flush=True)


if __name__ == "__main__":
    main()
