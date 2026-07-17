"""Embedding generation for semantic caching.

This module provides embedding generation for semantic similarity matching.
Uses a stateless, fixed-dimension HashingVectorizer so embeddings are
deterministic and reproducible: identical input always yields the identical
vector, regardless of corpus history or which instance produced it. (A prior
TF-IDF implementation refit on every newly-seen text, making embeddings drift
with the corpus -- see C-5.)

An optional MiniLM-L6-v2 backend (384-dim, Apple Neural Engine) is available
via ``backend="minilm"``.  It requires the ``mlx-embeddings`` package (install
with ``pip install -e ".[mlx]"``).  When the package is absent the constructor
silently falls back to the ``"hashing"`` backend so CI and non-Apple platforms
are unaffected.
"""

from __future__ import annotations

from typing import Dict, List, Literal

import numpy as np
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ---------------------------------------------------------------------------
# MiniLM lazy singleton — loaded once on first use, never on import.
# ---------------------------------------------------------------------------

_minilm_model = None  # type: ignore[var-annotated]
_minilm_available: bool | None = None  # None = not yet checked


def _try_load_minilm() -> bool:
    """Attempt to import and warm-up the MiniLM model.

    Returns True if the model is ready, False if the dependency is missing.
    Sets the module-level ``_minilm_model`` and ``_minilm_available`` globals.
    """
    global _minilm_model, _minilm_available
    if _minilm_available is not None:
        return _minilm_available
    try:
        import mlx_embeddings  # noqa: F401 – checked below

        # Apple MLX models are loaded via a model ID string.
        from mlx_embeddings import load  # type: ignore[import]

        _minilm_model = load("sentence-transformers/all-MiniLM-L6-v2")
        _minilm_available = True
    except (ImportError, Exception):  # ImportError or model-load failure
        _minilm_available = False
    return _minilm_available  # type: ignore[return-value]


def _embed_minilm(text: str) -> np.ndarray:
    """Encode *text* with MiniLM-L6-v2 via Apple MLX.

    Returns a normalised float32 vector of shape ``(384,)``.
    """
    from mlx_embeddings import embed  # type: ignore[import]

    result = embed([text], _minilm_model)
    # mlx_embeddings returns an mlx.core.array; convert to numpy float32.
    vec: np.ndarray = np.array(result[0], dtype=np.float32)
    norm = np.linalg.norm(vec)
    if norm > 1e-9:
        vec = vec / norm
    return vec


# ---------------------------------------------------------------------------
# EmbeddingGenerator
# ---------------------------------------------------------------------------

_Backend = Literal["hashing", "minilm"]

_HASHING_DIM = 1000
_MINILM_DIM = 384


class EmbeddingGenerator:
    """Generate deterministic embeddings for text.

    By default (``backend="hashing"``) uses a stateless, fixed-dimension
    ``HashingVectorizer`` which is lightweight, CPU-only, and requires no extra
    dependencies.

    When ``backend="minilm"`` is requested *and* ``mlx-embeddings`` is
    installed, the generator uses ``sentence-transformers/all-MiniLM-L6-v2``
    via Apple MLX (384-dim, Apple Neural Engine, ~2–4 ms/call warm).  If
    ``mlx-embeddings`` is not installed the constructor emits a warning and
    silently falls back to ``"hashing"``.

    The two backends are **not interchangeable**: their output dimensionality
    differs (1000 vs 384).  Callers that persist vectors on disk (e.g.
    ``PersistentEmbeddingIndex``) detect a dimension mismatch on load and
    trigger a full rebuild automatically.

    Note: the fixed hashing feature space means distinct short texts can collide
    to the same vector. Exact-match correctness therefore does not rely on the
    embedding -- ``SemanticCache.get()`` has an exact-key fast-path; the
    embedding is only used for approximate (fuzzy) matching.

    Attributes:
        vectorizer: Stateless HashingVectorizer (no fit, no vocabulary)
        corpus: List of texts recorded for logging / drift bookkeeping only
        embeddings_cache: Cache of generated embeddings
    """

    def __init__(
        self,
        max_features: int = _HASHING_DIM,
        max_corpus_size: int = 1000,
        backend: _Backend = "hashing",
    ):
        """Initialise the embedding generator.

        Args:
            max_features: Embedding dimensionality for the *hashing* backend.
                Ignored when ``backend="minilm"`` (dimensionality is fixed at
                384 by the model).
            max_corpus_size: Maximum tracked corpus size before LRU eviction.
                The corpus is bookkeeping only (used for logging / drift
                monitoring); it no longer influences the embedding.
            backend: ``"hashing"`` (default) or ``"minilm"``.  When
                ``"minilm"`` is requested but ``mlx-embeddings`` is absent the
                generator warns and falls back to ``"hashing"``.
        """
        self.max_corpus_size = max_corpus_size

        # Resolve the backend — fall back gracefully if mlx is missing.
        resolved_backend: _Backend = backend
        if backend == "minilm" and not _try_load_minilm():
            import warnings

            warnings.warn(
                "mlx-embeddings is not installed or failed to load; "
                "falling back to 'hashing' backend.  "
                "Install with: pip install -e '[mlx]'",
                stacklevel=2,
            )
            resolved_backend = "hashing"

        self._backend: _Backend = resolved_backend

        if self._backend == "hashing":
            self.max_features = max_features
            # Stateless + fixed-dimension: no fit, no vocabulary, so
            # transform() is a pure function of the input text.  This is what
            # makes embeddings deterministic and reproducible across corpus
            # growth and instances.
            self.vectorizer = HashingVectorizer(
                n_features=max_features,
                ngram_range=(1, 2),
                norm="l2",
                alternate_sign=False,
                stop_words="english",
            )
        else:
            # MiniLM: model is already loaded by _try_load_minilm().
            self.max_features = _MINILM_DIM
            self.vectorizer = None  # type: ignore[assignment]

        self.corpus: List[str] = []
        self.embeddings_cache: Dict[str, np.ndarray] = {}
        # No fitting is required for HashingVectorizer or MiniLM; always ready.
        self._fitted = True

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def embedding_dim(self) -> int:
        """Output dimensionality of the current backend.

        Returns:
            384 for ``"minilm"``, ``max_features`` (default 1000) for
            ``"hashing"``.
        """
        return _MINILM_DIM if self._backend == "minilm" else self.max_features

    def fit(self, texts: List[str]) -> None:
        """Record texts into the tracked corpus.

        Retained for API compatibility. The HashingVectorizer is stateless, so
        there is nothing to fit; this only records corpus membership (used for
        logging and vocabulary-drift bookkeeping).

        Args:
            texts: List of texts to record
        """
        if not texts:
            raise ValueError("Cannot fit on empty corpus")

        for text in texts:
            if text not in self.corpus:
                self.corpus.append(text)
        self._fitted = True

    def generate(self, text: str, use_cache: bool = True) -> np.ndarray:
        """Generate a deterministic embedding for *text*.

        Args:
            text: Text to generate embedding for
            use_cache: Whether to use cached embeddings

        Returns:
            Numpy array embedding vector of length ``embedding_dim``
        """
        # Handle empty or whitespace-only text: fixed-dimension zero vector.
        if not text or not text.strip():
            return np.zeros(self.embedding_dim)

        # Check cache first
        if use_cache and text in self.embeddings_cache:
            return self.embeddings_cache[text]

        # Track corpus membership for logging / drift bookkeeping only.
        if text not in self.corpus:
            if len(self.corpus) >= self.max_corpus_size:
                removed_text = self.corpus.pop(0)
                self.embeddings_cache.pop(removed_text, None)
            self.corpus.append(text)

        # Produce the embedding via the resolved backend.
        if self._backend == "minilm":
            embedding = _embed_minilm(text)
        else:
            # Pure transform: identical text -> identical vector, always.
            embedding = self.vectorizer.transform([text]).toarray()[0]

        # Cache if requested
        if use_cache:
            self.embeddings_cache[text] = embedding

        return embedding

    def generate_batch(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings for multiple texts.

        Args:
            texts: List of texts to generate embeddings for

        Returns:
            List of embedding vectors
        """
        if not self._fitted:
            self.fit(texts)

        if self._backend == "minilm":
            return [self.generate(t, use_cache=False) for t in texts]

        embeddings = self.vectorizer.transform(texts).toarray()
        return [embeddings[i] for i in range(len(texts))]

    def similarity(self, text1: str, text2: str) -> float:
        """Calculate cosine similarity between two texts.

        Args:
            text1: First text
            text2: Second text

        Returns:
            Cosine similarity score (0-1)
        """
        emb1 = self.generate(text1)
        emb2 = self.generate(text2)

        # Reshape for sklearn
        emb1 = emb1.reshape(1, -1)
        emb2 = emb2.reshape(1, -1)

        return float(cosine_similarity(emb1, emb2)[0][0])

    def most_similar(
        self, text: str, candidates: List[str], top_k: int = 5
    ) -> List[tuple[str, float]]:
        """Find most similar texts from candidates.

        Args:
            text: Query text
            candidates: List of candidate texts
            top_k: Number of top results to return

        Returns:
            List of (text, similarity_score) tuples, sorted by similarity
        """
        if not candidates:
            return []

        query_emb = self.generate(text)
        candidate_embs = self.generate_batch(candidates)

        # Calculate similarities
        similarities = []
        for i, candidate_emb in enumerate(candidate_embs):
            query_reshaped = query_emb.reshape(1, -1)
            candidate_reshaped = candidate_emb.reshape(1, -1)
            sim = float(cosine_similarity(query_reshaped, candidate_reshaped)[0][0])
            similarities.append((candidates[i], sim))

        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)

        return similarities[:top_k]

    def clear_cache(self) -> None:
        """Clear embeddings cache."""
        self.embeddings_cache.clear()

    def cache_size(self) -> int:
        """Get number of cached embeddings.

        Returns:
            Number of cached embeddings
        """
        return len(self.embeddings_cache)


def cosine_similarity_vectors(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Calculate cosine similarity between two vectors.

    Args:
        vec1: First vector
        vec2: Second vector

    Returns:
        Cosine similarity score (0-1)
    """
    # Handle zero vectors
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    # Calculate cosine similarity
    dot_product = np.dot(vec1, vec2)
    similarity = dot_product / (norm1 * norm2)

    # Clamp to [0, 1] range
    return float(max(0.0, min(1.0, similarity)))
