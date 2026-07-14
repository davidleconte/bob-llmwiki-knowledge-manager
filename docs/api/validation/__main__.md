# __main__

``python -m src.validation`` -- run the manifest-backed validation harness.

Builds one :class:`~src.facade.TokenOptimizer` from config, measures the real
product over a real corpus, writes ``report.json`` + ``manifest.json``, prints a
human summary, and exits non-zero if the honest gates fail (null test,
manifest completeness, tiktoken active). It holds no measurement logic itself.

## Functions

### `build_parser() -> argparse.ArgumentParser`


### `main(argv: Optional[Sequence[str]]) -> int`

