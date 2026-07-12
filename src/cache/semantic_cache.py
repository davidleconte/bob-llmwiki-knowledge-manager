"""Semantic similarity cache (L2) implementation.

This module implements a semantic similarity cache using embeddings and
cosine similarity. Provides approximate matches for semantically similar prompts.

Target metrics:
- Lookup latency: <100ms
- Similarity threshold: 0.85 (configurable)
- Hit rate contribution: ~5-8% of total 23.33%
"""

import time
from typing import Optional, Dict, Any, List, Tuple
import numpy as np

from src.cache.base import CacheInterface, CacheEntry, CacheStats
from src.cache.embeddings import EmbeddingGenerator, cosine_similarity_vectors


class SemanticCache(CacheInterface):
    """L2 cache for semantically similar prompts.
    
    Uses TF-IDF embeddings and cosine similarity to find similar prompts.
    Slower than exact cache but provides fuzzy matching.
    
    Attributes:
        similarity_threshold: Minimum similarity score (0-1) for cache hit
        max_size: Maximum number of entries
        embeddings: Dictionary mapping prompts to embeddings
        responses: Dictionary mapping prompts to responses
        metadata_store: Dictionary mapping prompts to metadata
        embedding_generator: Embedding generator instance
        stats: Cache statistics tracker
    """
    
    def __init__(self, 
                 similarity_threshold: float = 0.85,
                 max_size: int = 500):
        """Initialize semantic cache.
        
        Args:
            similarity_threshold: Minimum similarity for cache hit (0-1)
            max_size: Maximum number of entries before eviction
        """
        if not 0 <= similarity_threshold <= 1:
            raise ValueError("similarity_threshold must be between 0 and 1")
        if max_size <= 0:
            raise ValueError("max_size must be positive")
        
        self.similarity_threshold = similarity_threshold
        self.max_size = max_size
        
        # Storage
        self.embeddings: Dict[str, np.ndarray] = {}
        self.responses: Dict[str, str] = {}
        self.metadata_store: Dict[str, Dict[str, Any]] = {}
        self.entries: Dict[str, CacheEntry] = {}
        
        # Embedding generator
        self.embedding_generator = EmbeddingGenerator()
        
        # Statistics
        self._stats = CacheStats()
        self._similarity_scores: List[float] = []  # Track similarity scores for hits
    
    def get(self, key: str) -> Optional[str]:
        """Retrieve cached response for semantically similar key.
        
        Args:
            key: The cache key (prompt)
            
        Returns:
            Cached response if similar match found, None otherwise
        """
        # Check if query will cause vocabulary change
        will_change_vocab = key not in self.embedding_generator.corpus
        
        # Generate embedding for query
        query_embedding = self.embedding_generator.generate(key)
        
        # If vocabulary changed, regenerate all cached embeddings
        if will_change_vocab and len(self.embeddings) > 0:
            self._regenerate_all_embeddings()
        
        # Find most similar cached prompt
        best_match = None
        best_similarity = 0.0
        
        for cached_prompt, cached_embedding in self.embeddings.items():
            similarity = cosine_similarity_vectors(query_embedding, cached_embedding)
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = cached_prompt
        
        # Check if best match exceeds threshold
        if best_match and best_similarity >= self.similarity_threshold:
            # Update entry access stats
            if best_match in self.entries:
                self.entries[best_match].access()
            
            # Record hit and similarity score
            self._stats.record_hit()
            self._similarity_scores.append(best_similarity)
            
            return self.responses[best_match]
        
        # Record miss
        self._stats.record_miss()
        return None
    
    def set(self, key: str, response: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Store response in cache with embedding.
        
        Args:
            key: The cache key (prompt)
            response: The response to cache
            metadata: Optional metadata
        """
        # Check if we need to evict
        if key not in self.embeddings and len(self.embeddings) >= self.max_size:
            self._evict_lru()
        
        # Check if this is a new key that will cause vocabulary change
        is_new_key = key not in self.embeddings
        
        # Generate and store embedding
        embedding = self.embedding_generator.generate(key)
        self.embeddings[key] = embedding
        
        # If vocabulary changed (new key added), regenerate all embeddings
        # to ensure consistent dimensions
        if is_new_key and len(self.embeddings) > 1:
            self._regenerate_all_embeddings()
        
        # Store response and metadata
        self.responses[key] = response
        if metadata is None:
            metadata = {}
        self.metadata_store[key] = metadata
        
        # Create cache entry
        entry = CacheEntry(
            response=response,
            metadata=metadata,
            timestamp=time.time()
        )
        self.entries[key] = entry
    
    def _regenerate_all_embeddings(self) -> None:
        """Regenerate all embeddings to ensure consistent dimensions."""
        # Get all keys
        keys = list(self.embeddings.keys())
        
        # Clear embeddings
        self.embeddings.clear()
        
        # Regenerate each embedding
        for key in keys:
            embedding = self.embedding_generator.generate(key, use_cache=False)
            self.embeddings[key] = embedding
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if not self.entries:
            return
        
        # Find entry with oldest last_access time
        lru_key = min(self.entries.keys(), 
                     key=lambda k: self.entries[k].last_access)
        
        # Remove from all stores
        del self.embeddings[lru_key]
        del self.responses[lru_key]
        del self.metadata_store[lru_key]
        del self.entries[lru_key]
        
        self._stats.record_eviction()
    
    def clear(self) -> None:
        """Clear all entries from cache."""
        self.embeddings.clear()
        self.responses.clear()
        self.metadata_store.clear()
        self.entries.clear()
        self._stats.reset()
        self._similarity_scores.clear()
        self.embedding_generator.clear_cache()
    
    def size(self) -> int:
        """Get number of entries in cache.
        
        Returns:
            Number of cached entries
        """
        return len(self.embeddings)
    
    def hit_rate(self) -> float:
        """Calculate cache hit rate.
        
        Returns:
            Hit rate as percentage (0-100)
        """
        return self._stats.hit_rate()
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        avg_similarity = (
            sum(self._similarity_scores) / len(self._similarity_scores)
            if self._similarity_scores else 0.0
        )
        
        return {
            **self._stats.to_dict(),
            "size": self.size(),
            "max_size": self.max_size,
            "utilization": (self.size() / self.max_size) * 100,
            "similarity_threshold": self.similarity_threshold,
            "avg_similarity_score": avg_similarity,
            "embedding_cache_size": self.embedding_generator.cache_size(),
        }
    
    def find_similar(self, key: str, top_k: int = 5) -> List[Tuple[str, float, str]]:
        """Find top-k most similar cached prompts.
        
        Args:
            key: Query prompt
            top_k: Number of results to return
            
        Returns:
            List of (prompt, similarity, response) tuples
        """
        if not self.embeddings:
            return []
        
        # Check if query will cause vocabulary change
        will_change_vocab = key not in self.embedding_generator.corpus
        
        query_embedding = self.embedding_generator.generate(key)
        
        # If vocabulary changed, regenerate all cached embeddings
        if will_change_vocab and len(self.embeddings) > 0:
            self._regenerate_all_embeddings()
        
        # Calculate similarities for all cached prompts
        similarities = []
        for cached_prompt, cached_embedding in self.embeddings.items():
            similarity = cosine_similarity_vectors(query_embedding, cached_embedding)
            response = self.responses[cached_prompt]
            similarities.append((cached_prompt, similarity, response))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]
    
    def get_with_similarity(self, key: str) -> Optional[Tuple[str, float]]:
        """Get cached response with similarity score.
        
        Args:
            key: The cache key (prompt)
            
        Returns:
            Tuple of (response, similarity_score) if found, None otherwise
        """
        # Check if query will cause vocabulary change
        will_change_vocab = key not in self.embedding_generator.corpus
        
        query_embedding = self.embedding_generator.generate(key)
        
        # If vocabulary changed, regenerate all cached embeddings
        if will_change_vocab and len(self.embeddings) > 0:
            self._regenerate_all_embeddings()
        
        best_match = None
        best_similarity = 0.0
        
        for cached_prompt, cached_embedding in self.embeddings.items():
            similarity = cosine_similarity_vectors(query_embedding, cached_embedding)
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = cached_prompt
        
        if best_match and best_similarity >= self.similarity_threshold:
            return (self.responses[best_match], best_similarity)
        
        return None
    
    def contains_similar(self, key: str) -> bool:
        """Check if semantically similar key exists in cache.
        
        Args:
            key: The cache key
            
        Returns:
            True if similar key exists, False otherwise
        """
        result = self.get_with_similarity(key)
        return result is not None
    
    def update_threshold(self, new_threshold: float) -> None:
        """Update similarity threshold.
        
        Args:
            new_threshold: New threshold value (0-1)
        """
        if not 0 <= new_threshold <= 1:
            raise ValueError("threshold must be between 0 and 1")
        
        self.similarity_threshold = new_threshold
    
    def get_entry(self, key: str) -> Optional[CacheEntry]:
        """Get full cache entry.
        
        Args:
            key: The cache key
            
        Returns:
            CacheEntry if found, None otherwise
        """
        return self.entries.get(key)
    
    def average_similarity_score(self) -> float:
        """Get average similarity score for cache hits.
        
        Returns:
            Average similarity score (0-1)
        """
        if not self._similarity_scores:
            return 0.0
        return sum(self._similarity_scores) / len(self._similarity_scores)
