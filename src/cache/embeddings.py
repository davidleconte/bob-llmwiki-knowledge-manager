"""Embedding generation for semantic caching.

This module provides embedding generation for semantic similarity matching.
Uses simple TF-IDF vectors for fast, dependency-light embeddings.

For production, can be extended to use:
- OpenAI embeddings
- Sentence transformers
- Custom embedding models
"""

import numpy as np
from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class EmbeddingGenerator:
    """Generate embeddings for text using TF-IDF.
    
    This is a lightweight implementation suitable for semantic caching.
    For production use with large corpora, consider using pre-trained
    embedding models.
    
    Attributes:
        vectorizer: TF-IDF vectorizer
        corpus: List of texts used to fit vectorizer
        embeddings_cache: Cache of generated embeddings
    """
    
    def __init__(self, max_features: int = 1000, max_corpus_size: int = 1000):
        """Initialize embedding generator.
        
        Args:
            max_features: Maximum number of features for TF-IDF
            max_corpus_size: Maximum corpus size before LRU eviction (default: 1000)
        """
        self.max_features = max_features
        self.max_corpus_size = max_corpus_size
        self.vectorizer = None
        self.corpus: List[str] = []
        self.embeddings_cache: Dict[str, np.ndarray] = {}
        self._fitted = False
    
    def fit(self, texts: List[str]) -> None:
        """Fit vectorizer on corpus of texts.
        
        Args:
            texts: List of texts to fit on
        """
        if not texts:
            raise ValueError("Cannot fit on empty corpus")
        
        # Add new texts to corpus
        for text in texts:
            if text not in self.corpus:
                self.corpus.append(text)
        
        # Create vectorizer with appropriate parameters based on corpus size
        if len(self.corpus) == 1:
            # For single document, use simpler parameters
            self.vectorizer = TfidfVectorizer(
                max_features=self.max_features,
                ngram_range=(1, 2),
                min_df=1,
                max_df=1.0  # Allow all terms for single doc
            )
        else:
            # For multiple documents, use standard parameters
            self.vectorizer = TfidfVectorizer(
                max_features=self.max_features,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=1,
                max_df=0.95
            )
        
        # Fit on entire corpus
        self.vectorizer.fit(self.corpus)
        self._fitted = True
        
        # Clear cache when refitting
        self.embeddings_cache.clear()
    
    def generate(self, text: str, use_cache: bool = True) -> np.ndarray:
        """Generate embedding for text.
        
        Args:
            text: Text to generate embedding for
            use_cache: Whether to use cached embeddings
            
        Returns:
            Numpy array embedding vector
        """
        # Handle empty or whitespace-only text
        if not text or not text.strip():
            # Return zero vector of appropriate size
            if self._fitted and self.vectorizer is not None:
                vocab_size = len(self.vectorizer.vocabulary_)
                return np.zeros(min(vocab_size, self.max_features))
            else:
                # Default size if not fitted yet
                return np.zeros(self.max_features)
        
        # Check cache first
        if use_cache and text in self.embeddings_cache:
            return self.embeddings_cache[text]
        
        # Add to corpus and refit if this is a new text
        needs_refit = False
        if text not in self.corpus:
            # Implement LRU eviction if corpus exceeds max size
            if len(self.corpus) >= self.max_corpus_size:
                # Remove oldest entry (first in list)
                removed_text = self.corpus.pop(0)
                # Also remove from cache
                self.embeddings_cache.pop(removed_text, None)
                needs_refit = True  # Need to refit after removal
            
            self.corpus.append(text)
            needs_refit = True
        
        # Fit or refit if needed
        if not self._fitted or needs_refit:
            # Refit on entire corpus to maintain consistent dimensions
            if len(self.corpus) == 1:
                self.vectorizer = TfidfVectorizer(
                    max_features=self.max_features,
                    ngram_range=(1, 2),
                    min_df=1,
                    max_df=1.0
                )
            else:
                self.vectorizer = TfidfVectorizer(
                    max_features=self.max_features,
                    stop_words='english',
                    ngram_range=(1, 2),
                    min_df=1,
                    max_df=0.95
                )
            
            try:
                self.vectorizer.fit(self.corpus)
                self._fitted = True
                
                # Clear cache when refitting since dimensions may have changed
                self.embeddings_cache.clear()
            except ValueError as e:
                # Handle empty vocabulary error
                if "empty vocabulary" in str(e):
                    # Return zero vector
                    return np.zeros(self.max_features)
                raise
        
        # Generate embedding
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
