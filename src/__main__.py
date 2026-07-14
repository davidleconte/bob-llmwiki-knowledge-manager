"""Enable ``python -m src <command> ...`` by delegating to the CLI."""

from src.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
