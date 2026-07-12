# embeddings

Embedding generation for semantic caching.

This module provides embedding generation for semantic similarity matching.
Uses simple TF-IDF vectors for fast, dependency-light embeddings.

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

Generate embeddings for text using TF-IDF.

This is a lightweight implementation suitable for semantic caching.
For production use with large corpora, consider using pre-trained
embedding models.

Attributes:
    vectorizer: TF-IDF vectorizer
    corpus: List of texts used to fit vectorizer
    embeddings_cache: Cache of generated embeddings

#### Methods

##### `__init__(max_features: int)`

Initialize embedding generator.

Args:
    max_features: Maximum number of features for TF-IDF


##### `fit(texts: List[str]) -> None`

Fit vectorizer on corpus of texts.

Args:
    texts: List of texts to fit on


##### `generate(text: str, use_cache: bool) -> np.ndarray`

Generate embedding for text.

Args:
    text: Text to generate embedding for
    use_cache: Whether to use cached embeddings
    
Returns:
    Numpy array embedding vector


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


