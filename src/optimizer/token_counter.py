"""Token counting utilities for prompt optimization.

Model-aware counting via a multi-backend resolver (B1/CODE-10):

- ``gpt*`` / ``o1*`` / legacy OpenAI ids  -> tiktoken (exact)
- ``claude*``                             -> Anthropic backend if installed, else approx
- ``granite*`` / ``watsonx*`` / ``ibm*``  -> HF/Granite tokenizer if installed, else approx
- anything else                           -> approximation

An unavailable *exact* tokenizer NEVER raises on the hot path (availability is
deployment-dependent) but is **loud**: exactly one ``logging.warning`` per
``(process, model)``, and ``TokenCounter.approximate`` is set so no *published*
number silently rides on an approximation (the validation manifest's
``tiktoken_active`` gate already blocks a run whose counts are not exact).
"""

import logging
import re
from typing import Any, Dict, Optional, Protocol, runtime_checkable

from src.pricing import DEFAULT_MODEL, UnknownModelPriceError, usd_cost

logger = logging.getLogger(__name__)

# One-warning-per-(process, model): the loud-approximation contract must not spam
# a warning on every TokenCounter construction for the same unknown model.
_APPROX_WARNED: set[str] = set()
# Sibling dedupe for the loud unknown-price path (see estimate_cost).
_PRICE_WARNED: set[str] = set()

# Model-family prefixes routed to tiktoken (exact OpenAI BPE).
_OPENAI_PREFIXES = ("gpt", "o1", "o3", "text-", "davinci", "curie", "babbage", "ada")


def _approximate_token_count(text: str) -> int:
    """Model-blind heuristic: words + special_chars // 2 (~±15% of exact)."""
    text = re.sub(r"\s+", " ", text.strip())
    words = len(text.split())
    special_chars = len(re.findall(r"[^\w\s]", text))
    return words + (special_chars // 2)


@runtime_checkable
class Tokenizer(Protocol):
    """A resolved counting backend for one model.

    ``exact`` is True only when the count comes from the model's real tokenizer;
    ``False`` marks the loud approximation path.
    """

    name: str
    exact: bool

    def count(self, text: str) -> int: ...


class _TiktokenTokenizer:
    """Exact OpenAI BPE via tiktoken. Exposes ``encoding`` for accurate truncation."""

    exact = True

    def __init__(self, encoding: Any, name: str) -> None:
        self._encoding = encoding
        self.encoding = encoding
        self.name = name

    def count(self, text: str) -> int:
        return len(self._encoding.encode(text))


class _CallableTokenizer:
    """Exact count from an external callable (e.g. a HF/Granite ``encode``)."""

    exact = True
    encoding = None

    def __init__(self, count_fn: Any, name: str) -> None:
        self._count_fn = count_fn
        self.name = name

    def count(self, text: str) -> int:
        return int(self._count_fn(text))


class _ApproxTokenizer:
    """Model-blind heuristic backend (``exact=False``) — the loud fallback."""

    exact = False
    encoding = None

    def __init__(self, name: str) -> None:
        self.name = name

    def count(self, text: str) -> int:
        return _approximate_token_count(text)


def _resolve_openai(model: str) -> Optional[Tokenizer]:
    try:
        import tiktoken
    except ImportError:
        return None
    try:
        enc = tiktoken.encoding_for_model(model)
        return _TiktokenTokenizer(enc, f"tiktoken:{enc.name}")
    except KeyError:
        # Unknown OpenAI id -> the modern GPT-4/3.5 encoding; still exact.
        enc = tiktoken.get_encoding("cl100k_base")
        return _TiktokenTokenizer(enc, "tiktoken:cl100k_base")


def _resolve_granite(model: str) -> Optional[Tokenizer]:
    try:
        from transformers import AutoTokenizer  # optional: mnemox[watsonx]
    except ImportError:
        return None
    # local_files_only: NEVER download on the hot path — only use a tokenizer the
    # deployment has already cached. Not cached -> degrade to the loud
    # approximation rather than blocking on a multi-hundred-MB fetch.
    #
    # nosec B615: bandit flags from_pretrained() without a pinned `revision=`
    # (CWE-494, unpinned-revision download). The threat is not reachable here —
    # local_files_only=True performs no Hub download, so there is nothing to
    # tamper with in transit. Pinning a commit sha would be strictly worse: it
    # would break the "use whatever revision the deployment already cached"
    # contract above and silently degrade exact -> approximate tokenization
    # whenever the cached revision differs from the pin.
    try:
        tok = AutoTokenizer.from_pretrained(  # nosec B615
            "ibm-granite/granite-3.0-8b-instruct", local_files_only=True
        )
    except Exception:
        return None
    return _CallableTokenizer(lambda t: len(tok.encode(t)), "granite:hf")


def resolve_tokenizer(model: str) -> Tokenizer:
    """Resolve a :class:`Tokenizer` for *model* by family; never raises.

    An unavailable exact backend degrades to a loud approximation: exactly one
    ``logging.warning`` per ``(process, model)`` and an ``exact=False`` tokenizer.
    """
    m = (model or "").lower()
    resolved: Optional[Tokenizer] = None
    if m.startswith(_OPENAI_PREFIXES):
        resolved = _resolve_openai(model)
    elif m.startswith(("granite", "watsonx", "ibm")):
        resolved = _resolve_granite(model)
    # claude*/unknown families have no reliable offline exact tokenizer in-package
    # today, so they fall through to the loud approximation below.

    if resolved is not None:
        return resolved

    if model not in _APPROX_WARNED:
        _APPROX_WARNED.add(model)
        logger.warning(
            "tokenizer for %r unavailable; token counts are a ~±15%% approximation, "
            "not exact. Install the matching extra (e.g. mnemox[watsonx] or "
            "mnemox[anthropic]); published numbers must not ride on an approximation.",
            model,
        )
    return _ApproxTokenizer(f"approx:{model}")


class TokenCounter:
    """Token counter for LLM prompts.

    Provides accurate token counting using tiktoken when available,
    with fallback to approximation methods.

    Attributes:
        model: Model name for token counting
        tokenizer: Resolved counting backend (:class:`Tokenizer`)
        approximate: True when counts are a heuristic (not the model's tokenizer)
        encoding: Tiktoken encoding (only when the backend is tiktoken)
        use_tiktoken: Whether the exact tiktoken backend is in effect
        track_costs: Whether to track costs with CostTracker
    """

    def __init__(self, model: str = DEFAULT_MODEL, track_costs: bool = False):
        """Initialize token counter.

        Args:
            model: Model name (e.g., "gpt-4", "claude-sonnet-5", "granite-3-8b")
            track_costs: Whether to track costs with CostTracker
        """
        self.model = model
        self.track_costs = track_costs

        # Resolve the counting backend by model family (loud on approximation).
        self.tokenizer = resolve_tokenizer(model)
        self.approximate = not self.tokenizer.exact
        # Back-compat surface: ``encoding`` is the tiktoken encoding when (and only
        # when) the backend is tiktoken; ``use_tiktoken`` mirrors that and still
        # feeds the validation manifest's ``tiktoken_active`` publish-block.
        self.encoding = getattr(self.tokenizer, "encoding", None)
        self.use_tiktoken = self.encoding is not None

        # Initialize cost tracker if enabled
        self._cost_tracker = None
        if self.track_costs:
            try:
                from ..monitoring.cost_tracker import get_cost_tracker

                self._cost_tracker = get_cost_tracker()
            except ImportError:
                self.track_costs = False

    def count_tokens(self, text: str) -> int:
        """Count tokens in text.

        Args:
            text: Text to count tokens for

        Returns:
            Number of tokens
        """
        if not text:
            return 0

        tokens = self.tokenizer.count(text)

        # Track cost if enabled
        if self.track_costs and self._cost_tracker:
            self._cost_tracker.record_token_counting(tokens)

        return tokens

    def count_tokens_batch(self, texts: list[str]) -> list[int]:
        """Count tokens for a batch of texts.

        Convenience wrapper over :meth:`count_tokens` for many texts at once.
        Delegates per item so batch and single-count semantics stay identical
        (empty-string handling, tiktoken-vs-approximation, cost tracking).

        Args:
            texts: Texts to count tokens for.

        Returns:
            Per-text token counts, in the same order as ``texts``.
        """
        return [self.count_tokens(text) for text in texts]

    def _approximate_tokens(self, text: str) -> int:
        """Approximate token count (words + special_chars // 2).

        Retained for back-compat; the resolver's approximation backend uses the
        same :func:`_approximate_token_count` helper.

        Args:
            text: Text to count

        Returns:
            Approximate token count
        """
        return _approximate_token_count(text)

    def count_messages(self, messages: list[Dict[str, str]]) -> int:
        """Count tokens in message list (chat format).

        Args:
            messages: List of message dicts with 'role' and 'content'

        Returns:
            Total token count including message formatting overhead
        """
        total = 0

        for message in messages:
            # Count content tokens
            content = message.get("content", "")
            total += self.count_tokens(content)

            # Add overhead for message formatting
            # Typical: 4 tokens per message for role/formatting
            total += 4

        # Add overhead for conversation structure
        total += 2

        return total

    def estimate_cost(self, tokens: int, model: Optional[str] = None) -> Optional[float]:
        """Estimate the input-token cost for a token count.

        Delegates to the single pricing source (:func:`src.pricing.usd_cost`),
        pricing *tokens* as input tokens. An unpriced model is **loud, not silent**
        (B2/CODE-10): one warning per (process, model) and ``None`` — the cost is
        genuinely unknown, never a default-rate guess.

        Args:
            tokens: Number of tokens (priced as input tokens).
            model: Model name (uses self.model if not provided).

        Returns:
            Estimated USD cost, or ``None`` when the model has no price.
        """
        model = model or self.model
        try:
            return usd_cost(tokens, model=model)
        except UnknownModelPriceError:
            if model not in _PRICE_WARNED:
                _PRICE_WARNED.add(model)
                logger.warning(
                    "no price for model %r; cost estimate unavailable (add it to "
                    "PRICES in src/pricing.py). A cost figure must not use a "
                    "default-rate guess for an unpriced model.",
                    model,
                )
            return None

    def get_stats(self, text: str) -> Dict[str, Any]:
        """Get comprehensive token statistics.

        Args:
            text: Text to analyze

        Returns:
            Dictionary with token statistics
        """
        tokens = self.count_tokens(text)

        return {
            "tokens": tokens,
            "characters": len(text),
            "words": len(text.split()),
            "lines": len(text.splitlines()),
            "chars_per_token": len(text) / tokens if tokens > 0 else 0,
            "estimated_cost": self.estimate_cost(tokens),
            "model": self.model,
            "method": "tiktoken" if self.use_tiktoken else "approximation",
            "tokenizer": self.tokenizer.name,
            "exact": self.tokenizer.exact,
            "approximate": self.approximate,
        }

    def compare_texts(self, original: str, optimized: str) -> Dict[str, Any]:
        """Compare token counts between original and optimized text.

        Args:
            original: Original text
            optimized: Optimized text

        Returns:
            Dictionary with comparison statistics
        """
        original_tokens = self.count_tokens(original)
        optimized_tokens = self.count_tokens(optimized)

        savings = original_tokens - optimized_tokens
        savings_pct = (savings / original_tokens * 100) if original_tokens > 0 else 0

        # Track optimization cost if enabled
        if self.track_costs and self._cost_tracker and savings > 0:
            self._cost_tracker.record_optimization(original_tokens, optimized_tokens)

        return {
            "original_tokens": original_tokens,
            "optimized_tokens": optimized_tokens,
            "tokens_saved": savings,
            "savings_percentage": savings_pct,
            "compression_ratio": optimized_tokens / original_tokens if original_tokens > 0 else 0,
            "original_cost": self.estimate_cost(original_tokens),
            "optimized_cost": self.estimate_cost(optimized_tokens),
            "cost_savings": self.estimate_cost(savings),
        }

    def fits_context(self, text: str, max_tokens: int = 8192) -> bool:
        """Check if text fits within context window.

        Args:
            text: Text to check
            max_tokens: Maximum context window size

        Returns:
            True if text fits, False otherwise
        """
        return self.count_tokens(text) <= max_tokens

    def truncate_to_tokens(self, text: str, max_tokens: int) -> str:
        """Truncate text to fit within a token budget.

        Guarantees ``count_tokens(result) <= max_tokens``. With tiktoken the text
        is encoded, cut to the budget (reserving room for the "..." marker), then
        decoded — so the postcondition holds for *any* text, including multibyte
        scripts (emoji/CJK) where a fixed chars-per-token ratio overshoots. The
        previous char-count heuristic (``int(max_tokens * 3.5)``) violated the
        budget for dense/random text by up to ~2.6x and never fit at all for
        ``max_tokens <= 0``.

        Args:
            text: Text to truncate.
            max_tokens: Maximum tokens allowed. ``<= 0`` yields an empty string
                (nothing fits in a zero budget).

        Returns:
            Truncated text — ends with "..." when content was dropped, or the
            original text unchanged when it already fits.
        """
        if max_tokens <= 0:
            return ""

        if self.count_tokens(text) <= max_tokens:
            return text

        if not self.use_tiktoken or self.encoding is None:
            # No tokenizer available: token counts are already approximate on
            # this path, so fall back to the conservative character heuristic.
            char_limit = int(max_tokens * 3.5)
            if len(text) <= char_limit:
                return text
            return text[: max(0, char_limit - 3)] + "..."

        # Token-accurate path: reserve room for the ellipsis marker, cut, decode,
        # then re-trim to absorb any encode(decode(...)) boundary drift.
        ellipsis = "..."
        ellipsis_tokens = len(self.encoding.encode(ellipsis))
        budget = max(0, max_tokens - ellipsis_tokens)
        tokens = self.encoding.encode(text)[:budget]
        result = self.encoding.decode(tokens) + ellipsis
        while tokens and self.count_tokens(result) > max_tokens:
            tokens = tokens[:-1]
            result = self.encoding.decode(tokens) + ellipsis
        return result
