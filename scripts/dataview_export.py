"""
dataview_export.py — Inject semantic_links YAML frontmatter into exported KB documents.

Public API
----------
inject_dataview(export_path, graph_dict, top_n=0, min_weight=0.30) -> dict

No src/ imports. stdlib only.
"""

import os
import re
from pathlib import Path

# Matches the closing --- of a YAML frontmatter block.
# A frontmatter block starts at line 0 with "---" and ends at the next "---" line.
_FM_START_RE = re.compile(r'^---\s*\n', re.MULTILINE)
_FM_CLOSE_RE = re.compile(r'^---\s*$', re.MULTILINE)

# Matches an existing semantic_links: block (key + all following indented lines)
_SEMANTIC_LINKS_RE = re.compile(
    r'^semantic_links:[ \t]*\n(?:[ \t]+.*\n)*',
    re.MULTILINE,
)
# Also matches the scalar form: semantic_links: []
_SEMANTIC_LINKS_SCALAR_RE = re.compile(
    r'^semantic_links:[ \t]*\[\][ \t]*\n',
    re.MULTILINE,
)


def _build_neighbours(graph_dict: dict, min_weight: float, top_n: int) -> dict:
    """Return {doc_id: [(target, weight), ...]} for semantic edges above threshold."""
    neighbours: dict[str, list[tuple[str, float]]] = {}
    for edge in graph_dict.get("edges", []):
        if edge.get("type") != "semantic":
            continue
        w = edge.get("weight", 0.0)
        if w < min_weight:
            continue
        src = edge.get("source", "")
        tgt = edge.get("target", "")
        if not src or not tgt:
            continue
        neighbours.setdefault(src, []).append((tgt, w))

    # Sort descending by weight; cap at top_n if requested
    for doc_id in neighbours:
        neighbours[doc_id].sort(key=lambda t: t[1], reverse=True)
        if top_n > 0:
            neighbours[doc_id] = neighbours[doc_id][:top_n]

    return neighbours


def _render_semantic_links(links: list[tuple[str, float]]) -> str:
    """Render the semantic_links YAML block (with trailing newline)."""
    if not links:
        return "semantic_links: []\n"
    lines = ["semantic_links:\n"]
    for doc, weight in links:
        lines.append(f'  - doc: "{doc}"\n')
        lines.append(f"    weight: {round(weight, 2)}\n")
    return "".join(lines)


def _inject_into_content(content: str, links: list[tuple[str, float]]) -> str | None:
    """Return updated content with semantic_links injected/replaced, or None to skip."""
    # Must start with a frontmatter block
    if not content.startswith("---"):
        return None

    # Find closing ---: scan lines after the first
    lines = content.split("\n")
    close_idx = None
    for i in range(1, len(lines)):
        if re.match(r'^---\s*$', lines[i]):
            close_idx = i
            break

    if close_idx is None:
        return None  # No closing ---, skip

    # Extract frontmatter body (between opening and closing ---)
    fm_body = "\n".join(lines[1:close_idx])
    rest = "\n".join(lines[close_idx + 1:])  # everything after the closing ---

    # Build new semantic_links block
    new_block = _render_semantic_links(links)

    # Check if semantic_links already present in frontmatter
    if re.search(r'^semantic_links:', fm_body, re.MULTILINE):
        # Replace existing semantic_links block (key + all following indented lines,
        # or scalar form like `semantic_links: []`)
        def _replacer(m):
            return new_block
        # Try multi-line form first, then scalar form
        new_fm_body, n = _SEMANTIC_LINKS_RE.subn(new_block, fm_body + "\n")
        if n == 0:
            new_fm_body, _ = _SEMANTIC_LINKS_SCALAR_RE.subn(new_block, fm_body + "\n")
        new_fm_body = new_fm_body.rstrip("\n")
    else:
        # Insert before the closing ---
        new_fm_body = fm_body.rstrip("\n") + "\n" + new_block.rstrip("\n")

    # Reconstruct document
    rebuilt = "---\n" + new_fm_body + "\n---\n" + rest
    return rebuilt


def inject_dataview(
    export_path,
    graph_dict: dict,
    top_n: int = 0,
    min_weight: float = 0.30,
) -> dict:
    """Inject semantic_links YAML frontmatter into every .md in export_path.

    Parameters
    ----------
    export_path : str | Path
        Path to kb-export/knowledge-base/ (or any copy of the KB).
        MUST NOT point inside docs/knowledge-base/ — raises ValueError.
    graph_dict : dict
        Parsed kb-graph.json dict with "nodes" and "edges" keys.
    top_n : int
        Cap on neighbours per document (0 = unlimited above threshold).
    min_weight : float
        Minimum cosine weight to include a semantic edge.

    Returns
    -------
    dict
        {"files_annotated": int, "total_links": int}
    """
    export_path = Path(export_path).resolve()

    # Safety: must not point at the live KB
    live_kb = Path("docs/knowledge-base").resolve()
    if str(export_path).startswith(str(live_kb)):
        raise ValueError(
            f"export_path must not point inside the live KB at {live_kb}. "
            f"Got: {export_path}"
        )

    if not export_path.exists():
        raise FileNotFoundError(f"export_path does not exist: {export_path}")

    neighbours = _build_neighbours(graph_dict, min_weight, top_n)

    files_annotated = 0
    total_links = 0

    for root, _dirs, files in os.walk(export_path):
        root_path = Path(root)
        for fname in files:
            if not fname.endswith(".md"):
                continue
            file_path = root_path / fname
            # doc_id relative to export_path (e.g. "concepts/foo.md")
            doc_id = str(file_path.relative_to(export_path))

            content = file_path.read_text(encoding="utf-8")
            links = neighbours.get(doc_id, [])

            new_content = _inject_into_content(content, links)
            if new_content is None:
                # No frontmatter block — skip
                continue

            file_path.write_text(new_content, encoding="utf-8")
            files_annotated += 1
            total_links += len(links)

    return {"files_annotated": files_annotated, "total_links": total_links}
