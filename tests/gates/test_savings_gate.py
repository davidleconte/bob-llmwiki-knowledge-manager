"""ATK-GATE-03/01/05 regression: savings gate binding.

Tests:
  1. Bare "manifest" citation → unbacked (ATK-GATE-03).
  2. Fabricated figure with no backing → unbacked.
  3. Valid manifest path citation with in-tolerance value → backed.
  4. Non-existent manifest path → backed (path form accepted, no cross-check on missing file).
  5. Wrapped citation (claim on line N, path on line N+1) → backed (ATK-GATE-05).
  6. Value > 5 pp above a real manifest → not cross-checked when path doesn't exist.
"""


from scripts.check_savings_claims import (
    line_is_unbacked_claim,
    scan_text,
)

# ---------------------------------------------------------------------------
# ATK-GATE-03: bare "manifest" no longer backs a claim
# ---------------------------------------------------------------------------

def test_bare_manifest_is_unbacked():
    """'68.96% token savings (see manifest)' must be flagged (ATK-GATE-03)."""
    line = "Our optimizer delivers 68.96% token savings (see manifest)."
    assert line_is_unbacked_claim(line), (
        "Bare 'manifest' word must NOT back a savings claim (ATK-GATE-03)"
    )


def test_fabricated_with_no_backing_is_unbacked():
    """A fabricated savings figure with no citation must be flagged."""
    line = "Token savings: 68.96% (95% CI [66.42, 71.51])."
    assert line_is_unbacked_claim(line)


# ---------------------------------------------------------------------------
# ATK-GATE-03: manifest.json path form does back a claim
# ---------------------------------------------------------------------------

def test_manifest_json_path_backs_claim():
    """'manifest.json' path form must back a savings claim."""
    line = "Optimizer compression: mean 20.0% (manifest: evaluation/results/validation-2026-07-14/manifest.json)."
    assert not line_is_unbacked_claim(line), (
        "'manifest.json' path form must back the claim"
    )


def test_retraction_marker_backs_claim():
    """A retraction token must make a line non-flaggable."""
    line = 'The "68.96% / VALIDATED" figures were fabricated and are retracted.'
    assert not line_is_unbacked_claim(line)


# ---------------------------------------------------------------------------
# ATK-GATE-05: paragraph-level scanner (wrapped citations)
# ---------------------------------------------------------------------------

def test_wrapped_citation_not_flagged():
    """Claim on line N, manifest path on line N+1 → considered backed (ATK-GATE-05).

    scan_text look-ahead: if the next non-blank line backs the claim, don't flag.
    """
    text = (
        "Optimizer compression: mean 20.0%\n"
        "(manifest: evaluation/results/validation-2026-07-14/manifest.json)."
    )
    assert not scan_text(text), (
        "Wrapped manifest citation on continuation line must back the claim above (ATK-GATE-05)"
    )


def test_scan_text_paragraph_level():
    """scan_text must not flag a claim whose manifest path is on the next line."""
    text = (
        "## Results\n\n"
        "Optimizer compression: mean 20.0%\n"
        "(manifest: evaluation/results/validation-2026-07-14/manifest.json).\n\n"
        "More text here."
    )
    violations = scan_text(text)
    assert not violations, (
        f"scan_text should not flag the wrapped citation but got: {violations}"
    )


def test_genuinely_unbacked_is_flagged_by_scan():
    """scan_text must flag a claim with no citation at all."""
    text = "# Results\n\n- 89.3% token savings\n"
    violations = scan_text(text)
    assert violations, "Genuinely unbacked claim must be flagged by scan_text"


def test_banner_suppresses_scan():
    """A retraction banner in the file head must suppress all violations."""
    text = (
        "> **RETRACTED METRICS.** The 89.3% figure was fabricated.\n\n"
        "- 89.3% token savings\n"
    )
    assert not scan_text(text), "Bannered file must pass even with fabricated numbers"
