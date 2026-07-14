"""Library-layer CLI utilities (code-component analysis, batch file reading,
knowledge-base query).

These modules were relocated here from ``scripts/utils/`` in Phase 4 so that
in-package consumers — specifically the ``src/delegation`` agents — can import
them without an upward ``src/ -> scripts/`` dependency (the B3 layering
violation). Their nature is unchanged: they are operational CLI tools, still
invokable via the thin wrappers under ``scripts/utils/`` (which preserve the
documented ``python3 scripts/utils/<tool>.py`` entry points). Because they are
tooling rather than runtime library code, they are excluded from the coverage
gate and the mypy gate in ``pyproject.toml`` — the same treatment they had while
living under ``scripts/``.
"""
