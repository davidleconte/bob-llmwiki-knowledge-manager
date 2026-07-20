# limits

Global input-bound caps (A7 — DoS-surface hardening).

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

## Constants

- `MAX_FILE_BYTES`
- `MAX_CHUNKS_PER_DOC`
- `MAX_QUERY_CHARS`
- `MAX_GRAPH_NODES`
