# embeddings

Embedding generation for semantic caching.

This module provides embedding generation for semantic similarity matching.
Uses a stateless, fixed-dimension HashingVectorizer so embeddings are
deterministic and reproducible: identical input always yields the identical
vector, regardless of corpus history or which instance produced it. (A prior
TF-IDF implementation refit on every newly-seen text, making embeddings drift
with the corpus -- see C-5.)

For production, can be extended to use:
- OpenAI embeddings
- Sentence transformers
- Custom embedding models

## Functions

### `cosine_similarity_vectors(vec1: np.ndarray, vec2: np.ndarray) -> float`

Calculate cosine similarity between two vectors.

Args:
    vec1: First vector
    vec2: Second vector

Returns:
    Cosine similarity score (0-1)


## Classes

### `EmbeddingGenerator`

Generate deterministic embeddings for text using a HashingVectorizer.

This is a lightweight, stateless implementation suitable for semantic
caching. For production use with large corpora, consider using pre-trained
embedding models.

Note: the fixed hashing feature space means distinct short texts can collide
to the same vector. Exact-match correctness therefore does not rely on the
embedding -- ``SemanticCache.get()`` has an exact-key fast-path; the
embedding is only used for approximate (fuzzy) matching.

Attributes:
    vectorizer: Stateless HashingVectorizer (no fit, no vocabulary)
    corpus: List of texts recorded for logging / drift bookkeeping only
    embeddings_cache: Cache of generated embeddings

#### Methods

##### `__init__(max_features: int, max_corpus_size: int)`

Initialize embedding generator.

Args:
    max_features: Embedding dimensionality (fixed hashing feature space)
    max_corpus_size: Maximum tracked corpus size before LRU eviction.
        The corpus is bookkeeping only (used for logging / drift
        monitoring); it no longer influences the embedding.


##### `fit(texts: List[str]) -> None`

Record texts into the tracked corpus.

Retained for API compatibility. The HashingVectorizer is stateless, so
there is nothing to fit; this only records corpus membership (used for
logging and vocabulary-drift bookkeeping).

Args:
    texts: List of texts to record


##### `generate(text: str, use_cache: bool) -> np.ndarray`

Generate a deterministic embedding for text.

Args:
    text: Text to generate embedding for
    use_cache: Whether to use cached embeddings

Returns:
    Numpy array embedding vector of length ``max_features``


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


