# embeddings

Embedding generation for semantic caching.

This module provides embedding generation for semantic similarity matching.
Uses a stateless, fixed-dimension HashingVectorizer so embeddings are
deterministic and reproducible: identical input always yields the identical
vector, regardless of corpus history or which instance produced it. (A prior
TF-IDF implementation refit on every newly-seen text, making embeddings drift
with the corpus -- see C-5.)

An optional MiniLM-L6-v2 backend (384-dim) is available via ``backend="minilm"``.
It is activated by **either** of two optional packages (checked in order):

1. ``mlx-embeddings`` — Apple MLX, Apple Silicon only, ~2–4 ms/call warm.
   Install with ``pip install -e ".[mlx]"``.
2. ``sentence-transformers`` — cross-platform, CPU/GPU, ~5–20 ms/call warm.
   Install with ``pip install sentence-transformers``.

When neither package is installed the constructor warns and silently falls back
to the ``"hashing"`` backend so CI and non-Apple platforms are unaffected.

## Constants

- `_HASHING_DIM`
- `_MINILM_DIM`

## Functions

### `_try_load_minilm() -> bool`

Attempt to load MiniLM from mlx-embeddings, then sentence-transformers.

Returns True if the model is ready via either backend.
Sets the module-level ``_minilm_model``, ``_minilm_available``, and
``_minilm_backend`` globals.


### `_embed_minilm(text: str) -> np.ndarray`

Encode *text* with MiniLM-L6-v2 via the resolved backend.

Returns a normalised float32 vector of shape ``(384,)``.
Dispatches to Apple MLX or sentence-transformers depending on which
backend was loaded by ``_try_load_minilm()``.


### `cosine_similarity_vectors(vec1: np.ndarray, vec2: np.ndarray) -> float`

Calculate cosine similarity between two vectors.

Args:
    vec1: First vector
    vec2: Second vector

Returns:
    Cosine similarity score (0-1)


## Classes

### `EmbeddingGenerator`

Generate deterministic embeddings for text.

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

#### Methods

##### `__init__(max_features: int, max_corpus_size: int, backend: _Backend)`

Initialise the embedding generator.

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


##### `embedding_dim() -> int`

Output dimensionality of the current backend.

Returns:
    384 for ``"minilm"``, ``max_features`` (default 1000) for
    ``"hashing"``.


##### `fit(texts: List[str]) -> None`

Record texts into the tracked corpus.

Retained for API compatibility. The HashingVectorizer is stateless, so
there is nothing to fit; this only records corpus membership (used for
logging and vocabulary-drift bookkeeping).

Args:
    texts: List of texts to record


##### `generate(text: str, use_cache: bool) -> np.ndarray`

Generate a deterministic embedding for *text*.

Args:
    text: Text to generate embedding for
    use_cache: Whether to use cached embeddings

Returns:
    Numpy array embedding vector of length ``embedding_dim``


##### `generate_batch(texts: List[str]) -> List[np.ndarray]`

Generate embeddings for multiple texts.

Args:
    texts: List of texts to generate embeddings for

Returns:
    List of embedding vectors


##### `similarity(text1: str, text2: str) -> float`

Calculate cosine similarity between two texts.

Args:
    text1: First text
    text2: Second text

Returns:
    Cosine similarity score (0-1)


##### `most_similar(text: str, candidates: List[str], top_k: int) -> List[tuple[str, float]]`

Find most similar texts from candidates.

Args:
    text: Query text
    candidates: List of candidate texts
    top_k: Number of top results to return

Returns:
    List of (text, similarity_score) tuples, sorted by similarity


##### `clear_cache() -> None`

Clear embeddings cache.


##### `cache_size() -> int`

Get number of cached embeddings.

Returns:
    Number of cached embeddings


