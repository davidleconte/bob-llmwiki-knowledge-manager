"""Global input-bound caps (A7 — DoS-surface hardening).

Single home for the hard ceilings that bound resource use on adversarial or
accidentally-huge inputs. Nothing here is a tuning knob: raising a value widens
the denial-of-service surface, so each cap is documented with the resource it
bounds and the boundary that enforces it.

Information set / lookahead: these are enforcement ceilings applied at ingest and
query time on data already on disk or already supplied by the caller — they never
read future state and are independent of any per-run measurement.

One home per value: these constants are imported at every enforcement point
(never re-declared as literals). ``config/gates/gate-config.yaml`` carries a
review-routed ``input_bounds`` block that restates them for gate visibility, and
``scripts/check_value_homes.py`` fails CI if the two ever diverge — so weakening
a cap is conspicuous in a CODEOWNERS-reviewed file (the ATK-GATE-07 tie-in).
"""

from __future__ import annotations

# Maximum bytes read from a single KB file before it is skipped at ingest
# (embedding-index rebuild). Bounds per-file memory and the O(N) downstream work
# a single crafted file can inject. ~1 MiB of Markdown is far past any real doc.
MAX_FILE_BYTES = 1048576  # 1 MiB

# Maximum chunks emitted per document by MarkdownChunker. Bounds the embedding
# rows (and O(N) similarity work) that one doc with tens of thousands of ``##``
# headings can force into the index.
MAX_CHUNKS_PER_DOC = 500

# Maximum characters accepted from a raw query string before it is truncated at
# query entry. Bounds the embed / token cost of a pathological query. 8192 chars
# is ~2k tokens — orders of magnitude above any genuine search string.
MAX_QUERY_CHARS = 8192

# Maximum nodes admitted into an in-memory KnowledgeGraph before the builder
# stops growing it. Bounds PageRank / adjacency memory on a runaway corpus.
# Enforced at build (builder._add_nodes), not in the pure graph layer.
MAX_GRAPH_NODES = 20000
