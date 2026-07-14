# cli

Command-line interface for the token-optimization system.

A thin argparse front end over the :class:`~src.facade.TokenOptimizer` facade:
every subcommand constructs one facade from config and calls one already-tested
method, then prints the result. No business logic lives here.

Entry points:
    bob-optimize <command> ...     (console_scripts; see pyproject [project.scripts])
    python -m src <command> ...    (via src/__main__.py)

Component logging goes to stderr and is quieted to WARNING by default, so stdout
stays clean for piped/`--json` output; pass ``--verbose`` to restore INFO logs.

## Functions

### `_read_text(value: str) -> str`

Return the input text: read stdin when ``value`` is ``"-"``, else literal.


### `_emit(data: Any, as_json: bool) -> None`

Print a result either as indented JSON or as flat ``key: value`` lines.


### `build_parser() -> argparse.ArgumentParser`

Build the argument parser (also used directly by the tests).


### `main(argv: Optional[List[str]]) -> int`

CLI entry point. Returns a process exit code.

