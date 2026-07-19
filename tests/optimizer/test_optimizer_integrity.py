"""CODE-03/ATK-FS-03 regression: optimizer must never return empty, must preserve structure."""

from src.optimizer.prompt_optimizer import PromptOptimizer


def _make_optimizer(max_tokens: int) -> PromptOptimizer:
    return PromptOptimizer(max_tokens=max_tokens, use_cache=False)


# ---------------------------------------------------------------------------
# Never-empty post-condition (CODE-03)
# ---------------------------------------------------------------------------


def test_optimize_never_empty_for_long_input():
    """optimize() must not return empty string even for inputs >4096 tokens (CODE-03)."""
    # Build a ~5000-token input (rough: 1 word ≈ 1.3 tokens)
    long_text = " ".join(["word"] * 4000)
    optimizer = _make_optimizer(max_tokens=100)
    result = optimizer.optimize(long_text)
    assert result["optimized_text"], (
        "optimize() returned empty string for long input — CODE-03 not fixed"
    )
    assert len(result["optimized_text"].strip()) > 0


def test_optimize_never_empty_for_any_nonempty_input():
    """optimize() must not return empty for any non-empty input."""
    inputs = [
        "hello world",
        "a " * 100,
        "# Title\n\nContent here.\n\nMore content.",
        "x",
    ]
    optimizer = _make_optimizer(max_tokens=5)
    for text in inputs:
        result = optimizer.optimize(text)
        assert result["optimized_text"].strip(), (
            f"optimize() returned empty for input: {text[:50]!r}"
        )


# ---------------------------------------------------------------------------
# Structure preservation (CODE-07)
# ---------------------------------------------------------------------------


def test_frontmatter_preserved_through_optimization():
    """YAML frontmatter must survive _remove_redundancy (CODE-07)."""
    text = "---\ntitle: Test Document\ndate: 2026-07-19\ntrust_tier: verified\n---\n\n# Heading\n\nBody text here."
    optimizer = _make_optimizer(max_tokens=4096)
    result = optimizer.optimize(text)
    optimized = result["optimized_text"]
    assert "title: Test Document" in optimized, "Frontmatter title was stripped"
    assert "date: 2026-07-19" in optimized, "Frontmatter date was stripped"


def test_fenced_code_block_preserved_through_optimization():
    """Fenced code blocks must survive _remove_redundancy (CODE-07)."""
    text = (
        "# Doc\n\nSome text here.\n\n```python\ndef hello():\n    return 'hello'\n```\n\nMore text."
    )
    optimizer = _make_optimizer(max_tokens=4096)
    result = optimizer.optimize(text)
    optimized = result["optimized_text"]
    assert "```python" in optimized, "Code fence opening was stripped"
    assert "def hello():" in optimized, "Code fence content was stripped"
    assert "return 'hello'" in optimized, "Code fence content was stripped"


def test_multiline_structure_preserved():
    """Line breaks between paragraphs must be preserved (not collapsed to one line)."""
    text = "Paragraph one.\n\nParagraph two.\n\nParagraph three."
    optimizer = _make_optimizer(max_tokens=4096)
    result = optimizer.optimize(text)
    optimized = result["optimized_text"]
    # Must contain at least one blank line (newline between paragraphs)
    assert "\n" in optimized, "All newlines were collapsed — structure not preserved"


# ---------------------------------------------------------------------------
# Truncation flag (ATK-FS-03)
# ---------------------------------------------------------------------------


def test_truncated_flag_set_when_content_dropped():
    """result['truncated'] must be True when content is dropped (ATK-FS-03).

    Use a text where each line is unique (not repeated phrases), so truncation
    rather than redundancy removal is the mechanism that reduces size.
    """
    # Build many unique lines that cannot be deduplicated — forces truncation
    long_text = "\n".join(f"unique line {i} about topic {i} with content {i}" for i in range(300))
    optimizer = _make_optimizer(max_tokens=20)
    result = optimizer.optimize(long_text)
    assert result.get("truncated") is True, (
        "result['truncated'] not set when content was dropped — ATK-FS-03 not fixed\n"
        f"optimized_tokens={result.get('optimized_tokens')} original_tokens={result.get('original_tokens')}"
    )


def test_truncated_flag_false_for_short_input():
    """result['truncated'] must be False when no content is dropped."""
    optimizer = _make_optimizer(max_tokens=4096)
    result = optimizer.optimize("short text")
    assert result.get("truncated") is False, "result['truncated'] incorrectly True for short input"


def test_regression_3756_token_input():
    """Regression: a 3756-token input with max_tokens=100 must not return empty (CODE-03)."""
    # Build a markdown document that was observed to produce empty output
    sections = [
        "# Section {i}\n\nThis is content for section {i}. It discusses topic {i}.".format(i=i)
        for i in range(50)
    ]
    text = "\n\n".join(sections)
    optimizer = _make_optimizer(max_tokens=100)
    result = optimizer.optimize(text)
    assert result["optimized_text"].strip(), (
        "optimizer returned empty string for 3756-token-equivalent input — CODE-03 regression"
    )
