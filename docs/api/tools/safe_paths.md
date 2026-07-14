# safe_paths

Path-containment helper for the tool layer.

The ``src/tools`` utilities join a caller-supplied path onto a fixed base
directory (``ComponentAnalyzer.base_path``, ``KnowledgeBaseQuery.kb_path``,
``BatchFileReader.base_path``) and then read the result. Those paths reach the
tools untrusted — directly from each tool's own CLI and, for the delegation
agents, via ``task.target``. A bare ``base / user_path`` join lets an absolute
path or ``../`` sequence escape the base and read arbitrary files
(``Path("/base") / "../../etc/passwd"`` resolves to ``/etc/passwd``).

``resolve_within`` closes that hole: it joins, fully resolves (following ``..``
and symlinks), and returns the result only if it stays inside the base —
raising ``ValueError`` otherwise. This is the mitigation for the sole concrete
Information-Disclosure finding in the STRIDE threat model; see
``docs/security/THREAT_MODEL.md``.

## Functions

### `resolve_within(base: Path, untrusted: str) -> Path`

Resolve ``untrusted`` under ``base``, refusing any path that escapes it.

Args:
    base: The directory the result must stay inside. Resolved here, so the
        caller need not pre-resolve it.
    untrusted: A caller-supplied relative path. An absolute path, a ``../``
        sequence, or a symlink that points outside ``base`` all escape and
        are rejected.

Returns:
    The fully resolved, contained path (which may or may not exist yet —
    existence is the caller's check, as before).

Raises:
    ValueError: If the resolved path lies outside ``base``.

