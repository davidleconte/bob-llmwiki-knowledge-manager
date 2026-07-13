"""Semantic similarity cache (L2) implementation with version support.

This module implements a semantic similarity cache using embeddings and
cosine similarity. Provides approximate matches for semantically similar prompts.

Target metrics:
- Lookup latency: <100ms
- Similarity threshold: 0.85 (configurable)
- Hit rate contribution: ~5-8% of total 23.33%
"""

import time
import threading
from typing import Optional, Dict, Any, List, Tuple, Callable
import numpy as np

from src.cache.base import CacheInterface, CacheEntry, CacheStats
from src.cache.embeddings import EmbeddingGenerator, cosine_similarity_vectors
from src.monitoring import get_logger, get_metrics_collector


class SemanticCache(CacheInterface):
    """L2 cache for semantically similar prompts with version support.
    
    Uses TF-IDF embeddings and cosine similarity to find similar prompts.
    Slower than exact cache but provides fuzzy matching. Supports versioning
    for cache evolution without breaking existing cached data.
    
    Attributes:
        VERSION: Current cache version
        similarity_threshold: Minimum similarity score (0-1) for cache hit
        max_size: Maximum number of entries
        embeddings: Dictionary mapping versioned prompts to embeddings
        responses: Dictionary mapping versioned prompts to responses
        metadata_store: Dictionary mapping versioned prompts to metadata
        embedding_generator: Embedding generator instance
        stats: Cache statistics tracker
    """
    
    VERSION: str = "v1"  # Current cache version
    
    def __init__(self,
                 similarity_threshold: float = 0.85,
                 max_size: int = 500,
                 track_costs: bool = False,
                 ttl_seconds: Optional[float] = None,
                 clock: Callable[[], float] = time.time):
        """Initialize semantic cache.

        Args:
            similarity_threshold: Minimum similarity for cache hit (0-1)
            max_size: Maximum number of entries before eviction
            track_costs: Whether to track costs with CostTracker
            ttl_seconds: Optional entry time-to-live. When set, a matched entry
                older than this (by creation timestamp) is treated as a miss and
                evicted on read. ``None`` disables expiry (default).
            clock: Time source for stamping/expiry, injectable for
                deterministic tests. Defaults to ``time.time``.
        """
        if not 0 <= similarity_threshold <= 1:
            raise ValueError("similarity_threshold must be between 0 and 1")
        if max_size <= 0:
            raise ValueError("max_size must be positive")
        if ttl_seconds is not None and ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive when set")

        self.similarity_threshold = similarity_threshold
        self.max_size = max_size
        self.track_costs = track_costs
        self.ttl_seconds = ttl_seconds
        self._clock = clock
        
        # Thread safety lock
        self._lock = threading.RLock()
        
        # Storage (keys are versioned)
        self.embeddings: Dict[str, np.ndarray] = {}
        self.responses: Dict[str, str] = {}
        self.metadata_store: Dict[str, Dict[str, Any]] = {}
        self.entries: Dict[str, CacheEntry] = {}
        
        # Embedding generator
        self.embedding_generator = EmbeddingGenerator()
        
        # Statistics
        self._stats = CacheStats()
        self._similarity_scores: List[float] = []  # Track similarity scores for hits
        
        # Initialize monitoring
        self._logger = get_logger("cache.semantic")
        self._metrics = get_metrics_collector()
        
        # Initialize cost tracker if enabled
        self._cost_tracker = None
        if self.track_costs:
            try:
                from src.monitoring.cost_tracker import get_cost_tracker
                self._cost_tracker = get_cost_tracker()
            except ImportError:
                self.track_costs = False
        
        self._logger.info("semantic_cache_initialized", 
                        similarity_threshold=similarity_threshold,
                        max_size=max_size,
                        track_costs=track_costs,
                        version=self.VERSION)
    
    def _make_versioned_key(self, key: str, version: Optional[str] = None) -> str:
        """Create versioned cache key.
        
        Args:
            key: Base key (prompt)
            version: Version string (defaults to current VERSION)
            
        Returns:
            Versioned key string
        """
        if version is None:
            version = self.VERSION
        return f"{version}:{key}"
    
    def _extract_base_key(self, versioned_key: str) -> str:
        """Extract base key from versioned key.
        
        Args:
            versioned_key: Versioned key (format: "version:key")
            
        Returns:
            Base key without version prefix
        """
        if ':' in versioned_key:
            return versioned_key.split(':', 1)[1]
        return versioned_key
    
    def _extract_version(self, versioned_key: str) -> str:
        """Extract version from versioned key.
        
        Args:
            versioned_key: Versioned key (format: "version:key")
            
        Returns:
            Version string
        """
        if ':' in versioned_key:
            return versioned_key.split(':', 1)[0]
        return self.VERSION
    
    def get(self, key: str, version: Optional[str] = None) -> Optional[str]:
        """Retrieve cached response for semantically similar key.
        
        Thread-safe: Uses lock to protect shared state.
        
        Args:
            key: The cache key (prompt)
            version: Optional version (defaults to current VERSION)
            
        Returns:
            Cached response if similar match found, None otherwise
        """
        start_time = time.time()
        target_version = version or self.VERSION
        
        with self._lock:
            # Check if query will cause vocabulary change
            will_change_vocab = key not in self.embedding_generator.corpus
            
            # Generate embedding for query
            query_embedding = self.embedding_generator.generate(key)
            
            # If vocabulary changed, regenerate all cached embeddings
            if will_change_vocab and len(self.embeddings) > 0:
                self._regenerate_all_embeddings()
            
            # Find most similar cached prompt (only within target version)
            best_match = None
            best_similarity = 0.0
            
            for versioned_prompt, cached_embedding in self.embeddings.items():
                # Only consider entries from target version
                if self._extract_version(versioned_prompt) != target_version:
                    continue
                
                similarity = cosine_similarity_vectors(query_embedding, cached_embedding)
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = versioned_prompt
        
            latency_ms = (time.time() - start_time) * 1000
            
            # Check if best match exceeds threshold
            if best_match and best_similarity >= self.similarity_threshold:
                # Enforce TTL: a stale match is expired -> evict and miss.
                if (self.ttl_seconds is not None and best_match in self.entries and
                        (self._clock() - self.entries[best_match].timestamp) > self.ttl_seconds):
                    self._remove_entry(best_match)
                    self._stats.record_miss()
                    self._metrics.record_cache_miss("L2")
                    self._logger.debug("cache_expired",
                                     cache_level="L2",
                                     version=target_version,
                                     ttl_seconds=self.ttl_seconds)
                    return None

                # Update entry access stats
                if best_match in self.entries:
                    self.entries[best_match].access()
                
                # Record hit and similarity score
                self._stats.record_hit()
                self._similarity_scores.append(best_similarity)
                
                # Record metrics
                self._metrics.record_cache_hit("L2", latency_ms)
                
                # Log hit
                self._logger.debug("cache_hit",
                                 cache_level="L2",
                                 version=target_version,
                                 similarity=best_similarity,
                                 latency_ms=latency_ms,
                                 vocab_changed=will_change_vocab)
                
                # Track cost savings if enabled
                if self.track_costs and self._cost_tracker and best_match in self.entries:
                    # Estimate tokens saved (from metadata if available)
                    tokens_saved = self.entries[best_match].metadata.get('tokens', 0)
                    if tokens_saved > 0:
                        self._cost_tracker.record_cache_hit(tokens_saved)
                
                return self.responses[best_match]
            
            # Record miss
            self._stats.record_miss()
            
            # Record metrics
            self._metrics.record_cache_miss("L2")
            
            # Log miss
            self._logger.debug("cache_miss",
                             cache_level="L2",
                             version=target_version,
                             best_similarity=best_similarity,
                             threshold=self.similarity_threshold,
                             latency_ms=latency_ms,
                             vocab_changed=will_change_vocab)
            
            return None
    
    def set(self, key: str, value: str, version: Optional[str] = None,
            metadata: Optional[Dict[str, Any]] = None) -> None:
        """Store response in cache with embedding.
        
        Thread-safe: Uses lock to protect shared state.
        
        Args:
            key: The cache key (prompt)
            value: The response to cache
            version: Optional version (defaults to current VERSION)
            metadata: Optional metadata
        """
        with self._lock:
            versioned_key = self._make_versioned_key(key, version)
            is_update = versioned_key in self.embeddings
            
            # Check if we need to evict
            if not is_update and len(self.embeddings) >= self.max_size:
                self._evict_lru()
            
            # Check if this is a new key that will cause vocabulary change
            is_new_key = versioned_key not in self.embeddings
            
            # Generate and store embedding
            embedding = self.embedding_generator.generate(key)
            self.embeddings[versioned_key] = embedding
            
            # If vocabulary changed (new key added), regenerate all embeddings
            # to ensure consistent dimensions
            if is_new_key and len(self.embeddings) > 1:
                self._regenerate_all_embeddings()
            
            # Store response and metadata
            self.responses[versioned_key] = value
            if metadata is None:
                metadata = {}
            
            # Add version to metadata
            metadata['version'] = version or self.VERSION
            self.metadata_store[versioned_key] = metadata
            
            # Create cache entry
            entry = CacheEntry(
                response=value,
                metadata=metadata,
                timestamp=self._clock()
            )
            self.entries[versioned_key] = entry
            
            # Update cache size metric
            self._metrics.update_cache_size("L2", len(self.embeddings))
            
            # Log cache set
            self._logger.debug("cache_set",
                             cache_level="L2",
                             version=version or self.VERSION,
                             is_update=is_update,
                             cache_size=len(self.embeddings),
                             vocab_size=len(self.embedding_generator.corpus),
                             response_length=len(value))
    
    def _regenerate_all_embeddings(self) -> None:
        """No-op retained for API/call-site compatibility (see body).

        Historically recomputed every cached embedding when the vocabulary
        changed; with the stateless HashingVectorizer that is unnecessary and
        was O(n^2). Kept callable, does nothing.
        """
        # Intentionally a no-op since C-5.
        #
        # In the TF-IDF era a new key changed the vocabulary, so every cached
        # embedding had to be recomputed against the new vocab. The embedding
        # generator is now a *stateless* HashingVectorizer: ``generate`` is a
        # pure function of its input, so regenerating reproduces byte-for-byte
        # identical vectors (verified). Doing that on every novel key made cache
        # population O(n^2) and timed out the scalability / stress tests
        # (tests/performance/test_optimizer_performance.py::...cache_scalability,
        # tests/concurrency/test_cache_concurrency.py::...stress_multilevel).
        # Embeddings therefore never need rebuilding; kept as a no-op so the
        # guarded call sites (and any external callers) remain valid.
        return
    
    def _remove_entry(self, versioned_key: str) -> None:
        """Remove a key from every store defensively.

        Thread-safe: Must be called with lock held. Used for TTL expiry.
        """
        self.embeddings.pop(versioned_key, None)
        self.responses.pop(versioned_key, None)
        self.metadata_store.pop(versioned_key, None)
        self.entries.pop(versioned_key, None)

    def _evict_lru(self) -> None:
        """Evict least recently used entry.

        Thread-safe: Must be called with lock held.
        """
        if not self.entries:
            return
        
        # Find entry with oldest last_access time
        lru_key = min(self.entries.keys(), 
                     key=lambda k: self.entries[k].last_access)
        
        evicted_entry = self.entries[lru_key]
        evicted_version = self._extract_version(lru_key)
        
        # Remove from all stores
        del self.embeddings[lru_key]
        del self.responses[lru_key]
        del self.metadata_store[lru_key]
        del self.entries[lru_key]
        
        self._stats.record_eviction()
        
        # Record metrics
        self._metrics.record_cache_eviction("L2")
        
        # Log eviction
        self._logger.debug("cache_eviction",
                         cache_level="L2",
                         version=evicted_version,
                         cache_size=len(self.embeddings),
                         access_count=evicted_entry.access_count)
    
    def clear(self) -> None:
        """Clear all entries from cache.
        
        Thread-safe: Uses lock to protect shared state.
        """
        with self._lock:
            entries_cleared = len(self.embeddings)
            self.embeddings.clear()
            self.responses.clear()
            self.metadata_store.clear()
            self.entries.clear()
            self._stats.reset()
            self._similarity_scores.clear()
            
            # Log clear
            self._logger.info("cache_cleared",
                            cache_level="L2",
                            entries_cleared=entries_cleared)
            self.embedding_generator.clear_cache()
    
    def size(self) -> int:
        """Get number of entries in cache.
        
        Thread-safe: Uses lock to protect shared state.
        
        Returns:
            Number of cached entries
        """
        with self._lock:
            return len(self.embeddings)
    
    def hit_rate(self) -> float:
        """Calculate cache hit rate.
        
        Returns:
            Hit rate as percentage (0-100)
        """
        return self._stats.hit_rate()
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Thread-safe: Uses lock to protect shared state.
        
        Returns:
            Dictionary with cache statistics
        """
        with self._lock:
            avg_similarity = (
                sum(self._similarity_scores) / len(self._similarity_scores)
                if self._similarity_scores else 0.0
            )
            
            size = len(self.embeddings)
            
            return {
                **self._stats.to_dict(),
                "size": size,
                "max_size": self.max_size,
                "utilization": (size / self.max_size) * 100,
                "similarity_threshold": self.similarity_threshold,
                "avg_similarity_score": avg_similarity,
                "embedding_cache_size": self.embedding_generator.cache_size(),
                "version": self.VERSION,
            }
    
    def find_similar(self, key: str, top_k: int = 5, 
                    version: Optional[str] = None) -> List[Tuple[str, float, str]]:
        """Find top-k most similar cached prompts.
        
        Thread-safe: Uses lock to protect shared state.
        
        Args:
            key: Query prompt
            top_k: Number of results to return
            version: Optional version to search within
            
        Returns:
            List of (prompt, similarity, response) tuples
        """
        with self._lock:
            if not self.embeddings:
                return []
            
            target_version = version or self.VERSION
            
            # Check if query will cause vocabulary change
            will_change_vocab = key not in self.embedding_generator.corpus
            
            query_embedding = self.embedding_generator.generate(key)
            
            # If vocabulary changed, regenerate all cached embeddings
            if will_change_vocab and len(self.embeddings) > 0:
                self._regenerate_all_embeddings()
            
            # Calculate similarities for all cached prompts in target version
            similarities = []
            for versioned_prompt, cached_embedding in self.embeddings.items():
                # Only consider entries from target version
                if self._extract_version(versioned_prompt) != target_version:
                    continue
                
                similarity = cosine_similarity_vectors(query_embedding, cached_embedding)
                base_prompt = self._extract_base_key(versioned_prompt)
                response = self.responses[versioned_prompt]
                similarities.append((base_prompt, similarity, response))
            
            # Sort by similarity (descending)
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            return similarities[:top_k]
    
    def get_with_similarity(self, key: str, version: Optional[str] = None) -> Optional[Tuple[str, float]]:
        """Get cached response with similarity score.
        
        Thread-safe: Uses lock to protect shared state.
        
        Args:
            key: The cache key (prompt)
            version: Optional version
            
        Returns:
            Tuple of (response, similarity_score) if found, None otherwise
        """
        with self._lock:
            target_version = version or self.VERSION
            
            # Check if query will cause vocabulary change
            will_change_vocab = key not in self.embedding_generator.corpus
            
            query_embedding = self.embedding_generator.generate(key)
            
            # If vocabulary changed, regenerate all cached embeddings
            if will_change_vocab and len(self.embeddings) > 0:
                self._regenerate_all_embeddings()
            
            best_match = None
            best_similarity = 0.0
            
            for versioned_prompt, cached_embedding in self.embeddings.items():
                # Only consider entries from target version
                if self._extract_version(versioned_prompt) != target_version:
                    continue
                
                similarity = cosine_similarity_vectors(query_embedding, cached_embedding)
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = versioned_prompt
            
            if best_match and best_similarity >= self.similarity_threshold:
                return (self.responses[best_match], best_similarity)
            
            return None
    
    def contains(self, key: str, version: Optional[str] = None) -> bool:
        """Check if semantically similar key exists in cache.
        
        Args:
            key: The cache key
            version: Optional version
            
        Returns:
            True if similar key exists, False otherwise
        """
        result = self.get_with_similarity(key, version)
        return result is not None
    
    def update_threshold(self, new_threshold: float) -> None:
        """Update similarity threshold.
        
        Args:
            new_threshold: New threshold value (0-1)
        """
        if not 0 <= new_threshold <= 1:
            raise ValueError("threshold must be between 0 and 1")
        
        self.similarity_threshold = new_threshold
    
    def get_entry(self, key: str, version: Optional[str] = None) -> Optional[CacheEntry]:
        """Get full cache entry.
        
        Args:
            key: The cache key
            version: Optional version
            
        Returns:
            CacheEntry if found, None otherwise
        """
        versioned_key = self._make_versioned_key(key, version)
        return self.entries.get(versioned_key)
    
    def average_similarity_score(self) -> float:
        """Get average similarity score for cache hits.
        
        Returns:
            Average similarity score (0-1)
        """
        if not self._similarity_scores:
            return 0.0
        return sum(self._similarity_scores) / len(self._similarity_scores)
    
    def migrate(self, from_version: str, to_version: str) -> int:
        """Migrate entries from one version to another.
        
        Thread-safe: Uses lock to protect shared state.
        Creates new versioned entries for all entries matching from_version.
        Original entries are preserved.
        
        Args:
            from_version: Source version
            to_version: Target version
            
        Returns:
            Number of entries migrated
        """
        with self._lock:
            migrated = 0
            entries_to_migrate = []
            
            # Collect entries to migrate
            for versioned_key, entry in self.entries.items():
                if self._extract_version(versioned_key) == from_version:
                    base_key = self._extract_base_key(versioned_key)
                    entries_to_migrate.append((base_key, entry))
        
        # Migrate entries (set() has its own lock)
        for base_key, entry in entries_to_migrate:
            # Create new versioned entry
            self.set(base_key, entry.response, to_version, entry.metadata.copy())
            migrated += 1
        
        self._logger.info("cache_migration",
                        from_version=from_version,
                        to_version=to_version,
                        migrated=migrated)
        
        return migrated
    
    def cleanup_version(self, version: str) -> int:
        """Remove all entries for a specific version.
        
        Thread-safe: Uses lock to protect shared state.
        
        Args:
            version: Version to clean up
            
        Returns:
            Number of entries removed
        """
        with self._lock:
            removed = 0
            keys_to_remove = []
            
            # Collect keys to remove
            for versioned_key in self.entries.keys():
                if self._extract_version(versioned_key) == version:
                    keys_to_remove.append(versioned_key)
            
            # Remove entries
            for versioned_key in keys_to_remove:
                if versioned_key in self.embeddings:
                    del self.embeddings[versioned_key]
                if versioned_key in self.responses:
                    del self.responses[versioned_key]
                if versioned_key in self.metadata_store:
                    del self.metadata_store[versioned_key]
                if versioned_key in self.entries:
                    del self.entries[versioned_key]
                removed += 1
            
            self._logger.info("version_cleanup",
                            version=version,
                            removed=removed)
            
            return removed
    
    def reset_stats(self) -> None:
        """Reset statistics counters."""
        self._stats.reset()
        self._similarity_scores.clear()