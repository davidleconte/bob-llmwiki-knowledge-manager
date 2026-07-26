"""Audit-2026-07-25: the committed-credential gate (ATK-SUP-09) must be able to fail.

This gate had never executed. It carries ``needs: [test]``, the coverage job was
hanging to GitHub's 6-hour ceiling and being cancelled, and across the last six runs
on ``main`` the secrets scan was ``skipped`` or ``cancelled`` every time. The first
run that reached it flagged two documentation lines that had been on ``main`` all
along.

These tests pin the replacement: an allowlist keyed on ``(path, digest-of-line)``
rather than a blanket ``grep -v knowledge-base/research`` directory exemption. The
distinction is the whole point — an exemption that cannot be aimed at one exact line
is an exemption anything can hide behind.
"""

from scripts.check_committed_secrets import (
    ALLOWLIST,
    credential_probe,
    line_digest,
    scan,
    scan_text,
    unexplained,
)

# ── The thing the gate exists to catch ───────────────────────────────────────────


def test_real_credential_is_flagged():
    hits = scan_text("src/config.py", credential_probe("passw0rd") + "\n")
    assert len(hits) == 1
    assert hits[0].key == "MQ_PASSWORD"


def test_credential_in_yaml_config_is_flagged():
    assert scan_text("config/broker.yaml", "  " + credential_probe("hunter2") + "\n")


# ── Things that must never be flagged ────────────────────────────────────────────


def test_placeholders_are_not_credentials():
    for line in (
        "MQ_PASSWORD=<your-password-here>",
        "MQ_PASSWORD=your-password",
        "MQ_PASSWORD=changeme",
        "MQ_PASSWORD=${BROKER_SECRET}",
        "MQ_PASSWORD=",
    ):
        assert not scan_text("config/app.yaml", line + "\n"), line


def test_template_files_are_out_of_scope():
    assert not scan_text(".env.template", credential_probe("passw0rd") + "\n")
    assert not scan_text("config/app.yaml.example", credential_probe("passw0rd") + "\n")


def test_lowercase_assignment_is_not_matched():
    """Scoped to the ATK-SUP-09 shape; a prose sentence must not trip it."""
    assert not scan_text("docs/guide.md", "set the mq_password=whatever you like\n")


# ── The allowlist must not be a skeleton key ─────────────────────────────────────


def _an_allowlisted_line() -> tuple[str, str]:
    """Return (path, the exact line) for one real allowlist entry."""
    from pathlib import Path

    from scripts.check_committed_secrets import REPO_ROOT

    path, digest = next(iter(ALLOWLIST))
    text = Path(REPO_ROOT / path).read_text(encoding="utf-8", errors="replace")
    line = next(ln for ln in text.splitlines() if line_digest(ln) == digest)
    return path, line


def test_allowlisted_line_passes_at_its_own_path():
    path, line = _an_allowlisted_line()
    assert not unexplained(scan_text(path, line + "\n"))


def test_same_text_in_another_file_still_fails():
    """The exemption is (path, line) — not the text, and not the directory."""
    _, line = _an_allowlisted_line()
    assert unexplained(scan_text("src/leaked.py", line + "\n"))


def test_editing_an_allowlisted_line_revokes_its_exemption():
    """A digest key means the exemption covers the line as reviewed, not the file."""
    path, line = _an_allowlisted_line()
    assert unexplained(scan_text(path, line + " " + credential_probe("hunter2") + "\n"))


def test_new_credential_in_an_allowlisted_file_still_fails():
    path, _ = _an_allowlisted_line()
    assert unexplained(scan_text(path, credential_probe("freshleak") + "\n"))


def test_research_dir_is_no_longer_blanket_exempt():
    """ATK-GATE-04: the old rule dropped every hit under knowledge-base/research."""
    assert unexplained(
        scan_text("docs/knowledge-base/research/notes.md", credential_probe("passw0rd") + "\n")
    )


# ── The live tree ────────────────────────────────────────────────────────────────


def test_live_tree_has_no_unexplained_credentials():
    bad = unexplained(scan())
    assert bad == [], "unexplained credential(s): " + ", ".join(f"{h.path}:{h.lineno}" for h in bad)


def test_no_credential_pattern_outside_markdown():
    """The finding register's claim — 'absent in code/config' — held as an assertion.

    Every known hit is prose about a resolved finding. If one ever appears in code or
    config, that is a different and much worse fact, and this fails independently of
    whatever the allowlist says.
    """
    offenders = [h for h in scan() if not h.path.endswith(".md")]
    assert offenders == [], "credential pattern in code/config: " + ", ".join(
        f"{h.path}:{h.lineno}" for h in offenders
    )
