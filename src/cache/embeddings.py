"""Embedding generation for semantic caching.

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
"""

from typing import Dict, List

import numpy as np
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class EmbeddingGenerator:
    """Generate deterministic embeddings for text using a HashingVectorizer.

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
    """

    def __init__(self, max_features: int = 1000, max_corpus_size: int = 1000):
        """Initialize embedding generator.

        Args:
            max_features: Embedding dimensionality (fixed hashing feature space)
            max_corpus_size: Maximum tracked corpus size before LRU eviction.
                The corpus is bookkeeping only (used for logging / drift
                monitoring); it no longer influences the embedding.
        """
        self.max_features = max_features
        self.max_corpus_size = max_corpus_size
        # Stateless + fixed-dimension: no fit, no vocabulary, so transform() is
        # a pure function of the input text. This is what makes embeddings
        # deterministic and reproducible across corpus growth and instances.
        self.vectorizer = HashingVectorizer(
            n_features=max_features,
            ngram_range=(1, 2),
            norm='l2',
            alternate_sign=False,
            stop_words='english',
        )
        self.corpus: List[str] = []
        self.embeddings_cache: Dict[str, np.ndarray] = {}
        # No fitting is required for a HashingVectorizer; always "ready".
        self._fitted = True

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
        """Generate a deterministic embedding for text.

        Args:
            text: Text to generate embedding for
            use_cache: Whether to use cached embeddings

        Returns:
            Numpy array embedding vector of length ``max_features``
        """
        # Handle empty or whitespace-only text: fixed-dimension zero vector.
        if not text or not text.strip():
            return np.zeros(self.max_features)

        # Check cache first
        if use_cache and text in self.embeddings_cache:
            return self.embeddings_cache[text]

        # Track corpus membership for logging / drift bookkeeping only. This no
        # longer affects the embedding (the vectorizer is stateless), so it does
        # NOT reintroduce the corpus-dependent drift that C-5 fixed.
        if text not in self.corpus:
            if len(self.corpus) >= self.max_corpus_size:
                removed_text = self.corpus.pop(0)
                self.embeddings_cache.pop(removed_text, None)
            self.corpus.append(text)

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

    def most_similar(self, text: str, candidates: List[str], top_k: int = 5) -> List[tuple[str, float]]:
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
