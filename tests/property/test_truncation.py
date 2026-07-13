"""Property-based test for the truncation invariant:

    ``count_tokens(truncate_to_tokens(text, N)) <= N``   for all text, all N >= 0.

This is now an *unconstrained* property: ``truncate_to_tokens`` was made
token-accurate (encode -> trim -> decode, reserving room for the "..." marker),
so the token budget is honored for any utf-8 text — including dense multibyte
scripts (emoji/CJK) and ``N == 0`` — not just low-density English. The previous
char-count heuristic (``int(N * 3.5)``) overshot the budget by up to ~2.6x on
random/dense text and never fit at all for ``N == 0``; the point-example
regression guards for those cases live in
``tests/optimizer/test_token_counter.py``.

The deterministic hypothesis profile is registered in ``tests/conftest.py``.
"""

from hypothesis import given
from hypothesis import strategies as st

from src.optimizer.token_counter import TokenCounter

# One shared counter: tiktoken cl100k_base (gpt-4) is deterministic and stateless
# for counting/encoding, so sharing across examples is safe and fast.
_counter = TokenCounter()

# Any utf-8-encodable text (excludes lone surrogates, which are not valid text).
_text = st.text(st.characters(codec="utf-8"))


@given(text=_text, max_tokens=st.integers(min_value=0, max_value=500))
def test_truncation_respects_token_budget(text, max_tokens):
    """The truncated output never exceeds the requested token budget."""
    result = _counter.truncate_to_tokens(text, max_tokens)
    assert _counter.count_tokens(result) <= max_tokens


@given(text=_text, max_tokens=st.integers(min_value=1, max_value=500))
def test_truncation_marks_dropped_content(text, max_tokens):
    """When content is dropped the result carries the "..." marker; text that
    already fits within the budget is returned unchanged."""
    result = _counter.truncate_to_tokens(text, max_tokens)
    if result != text:
        assert result.endswith("...")
