# report

Assemble and serialize the validation report.

The report keeps the three savings mechanisms in **separate, labelled** sections
and elevates only optimizer compression to the headline. It embeds the
reproducibility manifest and refuses to print "VALIDATED" -- it prints measured
numbers with their provenance and lets the reader judge.

## Constants

- `SCHEMA_VERSION`

## Functions

### `build_report(manifest: Dict[str, Any], optimizer: Dict[str, Any], cache: Dict[str, Any], truncation: Dict[str, Any], null_test: Dict[str, Any]) -> Dict[str, Any]`

Assemble the machine-readable report with a single, honest headline.


### `write_report(out_dir: Path, report: Dict[str, Any], manifest: Dict[str, Any]) -> Tuple[Path, Path]`

Write ``report.json`` and a sibling ``manifest.json``; return both paths.


### `human_summary(report: Dict[str, Any]) -> str`

Render a plain-text summary that leads with N and provenance.

