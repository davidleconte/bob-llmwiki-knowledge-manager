"""Vocabulary drift monitoring for semantic cache.

Tracks changes in TF-IDF vocabulary over time to detect concept drift
and trigger cache invalidation or retraining when needed.
"""

import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from src.monitoring.logger import get_logger


@dataclass
class VocabularySnapshot:
    """Snapshot of vocabulary at a point in time.

    Attributes:
        timestamp: When snapshot was taken
        vocabulary: Set of terms in vocabulary
        vocabulary_size: Number of terms
        corpus_size: Number of documents in corpus
        top_terms: Most common terms (optional)
    """

    timestamp: float
    vocabulary: Set[str]
    vocabulary_size: int
    corpus_size: int
    top_terms: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp,
            "vocabulary_size": self.vocabulary_size,
            "corpus_size": self.corpus_size,
            "top_terms": self.top_terms[:10],  # Top 10 only
        }


@dataclass
class DriftMetrics:
    """Metrics for vocabulary drift.

    Attributes:
        new_terms: Number of new terms added
        removed_terms: Number of terms removed
        total_change: Total vocabulary change (new + removed)
        change_rate: Rate of change (0-1)
        drift_score: Overall drift score (0-1)
    """

    new_terms: int
    removed_terms: int
    total_change: int
    change_rate: float
    drift_score: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "new_terms": self.new_terms,
            "removed_terms": self.removed_terms,
            "total_change": self.total_change,
            "change_rate": self.change_rate,
            "drift_score": self.drift_score,
        }


class VocabularyDriftMonitor:
    """Monitor vocabulary drift in semantic cache.

    Tracks vocabulary changes over time and detects significant drift
    that may require cache invalidation or model retraining.

    Attributes:
        drift_threshold: Threshold for significant drift (0-1)
        snapshot_interval: Minimum time between snapshots (seconds)
        max_snapshots: Maximum number of snapshots to keep
        snapshots: Historical vocabulary snapshots
    """

    def __init__(
        self,
        drift_threshold: float = 0.3,
        snapshot_interval: float = 300.0,
        max_snapshots: int = 100,
    ):
        """Initialize vocabulary drift monitor.

        Args:
            drift_threshold: Threshold for significant drift (0-1)
            snapshot_interval: Minimum time between snapshots (seconds)
            max_snapshots: Maximum number of snapshots to keep
        """
        if not 0 <= drift_threshold <= 1:
            raise ValueError("drift_threshold must be between 0 and 1")

        self.drift_threshold = drift_threshold
        self.snapshot_interval = snapshot_interval
        self.max_snapshots = max_snapshots

        self.snapshots: deque = deque(maxlen=max_snapshots)
        self._last_snapshot_time: float = 0.0
        self._drift_events: List[Dict[str, Any]] = []

        self._logger = get_logger("monitoring.vocabulary_drift")

        self._logger.info(
            "vocabulary_drift_monitor_initialized",
            drift_threshold=drift_threshold,
            snapshot_interval=snapshot_interval,
            max_snapshots=max_snapshots,
        )

    def take_snapshot(self, embedding_generator: Any) -> VocabularySnapshot:
        """Take a snapshot of current vocabulary.

        Args:
            embedding_generator: EmbeddingGenerator instance

        Returns:
            VocabularySnapshot
        """
        current_time = time.time()

        # Check if enough time has passed since last snapshot
        if current_time - self._last_snapshot_time < self.snapshot_interval:
            # Return last snapshot if available
            if self.snapshots:
                return self.snapshots[-1]

        # Get vocabulary from vectorizer. A stateless embedder (e.g.
        # HashingVectorizer) has no ``vocabulary_``; treat it as an empty
        # vocabulary rather than crashing -- a hashed embedder has no
        # enumerable vocabulary to drift.
        vocabulary = set()
        if embedding_generator.vectorizer is not None:
            vocab = getattr(embedding_generator.vectorizer, "vocabulary_", None)
            if vocab is not None:
                vocabulary = set(vocab.keys())

        # Get top terms if available
        top_terms = []
        if embedding_generator.vectorizer is not None and hasattr(
            embedding_generator.vectorizer, "get_feature_names_out"
        ):
            try:
                feature_names = embedding_generator.vectorizer.get_feature_names_out()
                top_terms = list(feature_names[:20])  # Top 20 terms
            except Exception:
                pass

        snapshot = VocabularySnapshot(
            timestamp=current_time,
            vocabulary=vocabulary,
            vocabulary_size=len(vocabulary),
            corpus_size=len(embedding_generator.corpus),
            top_terms=top_terms,
        )

        self.snapshots.append(snapshot)
        self._last_snapshot_time = current_time

        self._logger.debug(
            "vocabulary_snapshot_taken",
            vocabulary_size=snapshot.vocabulary_size,
            corpus_size=snapshot.corpus_size,
        )

        return snapshot

    def calculate_drift(
        self, old_snapshot: VocabularySnapshot, new_snapshot: VocabularySnapshot
    ) -> DriftMetrics:
        """Calculate drift between two snapshots.

        Args:
            old_snapshot: Earlier snapshot
            new_snapshot: Later snapshot

        Returns:
            DriftMetrics
        """
        old_vocab = old_snapshot.vocabulary
        new_vocab = new_snapshot.vocabulary

        # Calculate changes
        new_terms = len(new_vocab - old_vocab)
        removed_terms = len(old_vocab - new_vocab)
        total_change = new_terms + removed_terms

        # Calculate change rate (relative to old vocabulary size)
        if len(old_vocab) > 0:
            change_rate = total_change / len(old_vocab)
        else:
            change_rate = 1.0 if len(new_vocab) > 0 else 0.0

        # Calculate drift score (weighted by corpus size change)
        corpus_growth = new_snapshot.corpus_size - old_snapshot.corpus_size
        if old_snapshot.corpus_size > 0:
            corpus_growth_rate = corpus_growth / old_snapshot.corpus_size
        else:
            corpus_growth_rate = 1.0 if new_snapshot.corpus_size > 0 else 0.0

        # Drift score combines vocabulary change and corpus growth
        # Higher weight on vocabulary change (0.7) vs corpus growth (0.3)
        drift_score = (0.7 * change_rate) + (0.3 * min(corpus_growth_rate, 1.0))

        return DriftMetrics(
            new_terms=new_terms,
            removed_terms=removed_terms,
            total_change=total_change,
            change_rate=change_rate,
            drift_score=drift_score,
        )

    def check_drift(self, embedding_generator: Any) -> Optional[DriftMetrics]:
        """Check for vocabulary drift.

        Takes a new snapshot and compares with the most recent snapshot.

        Args:
            embedding_generator: EmbeddingGenerator instance

        Returns:
            DriftMetrics if drift detected, None otherwise
        """
        # Take new snapshot
        new_snapshot = self.take_snapshot(embedding_generator)

        # Need at least 2 snapshots to detect drift
        if len(self.snapshots) < 2:
            return None

        # Compare with previous snapshot
        old_snapshot = self.snapshots[-2]
        drift_metrics = self.calculate_drift(old_snapshot, new_snapshot)

        # Check if drift exceeds threshold
        if drift_metrics.drift_score >= self.drift_threshold:
            self._record_drift_event(drift_metrics, old_snapshot, new_snapshot)

            self._logger.warning(
                "vocabulary_drift_detected",
                drift_score=drift_metrics.drift_score,
                threshold=self.drift_threshold,
                new_terms=drift_metrics.new_terms,
                removed_terms=drift_metrics.removed_terms,
            )

            return drift_metrics

        return None

    def _record_drift_event(
        self,
        metrics: DriftMetrics,
        old_snapshot: VocabularySnapshot,
        new_snapshot: VocabularySnapshot,
    ) -> None:
        """Record a drift event.

        Args:
            metrics: Drift metrics
            old_snapshot: Old vocabulary snapshot
            new_snapshot: New vocabulary snapshot
        """
        event = {
            "timestamp": new_snapshot.timestamp,
            "metrics": metrics.to_dict(),
            "old_vocabulary_size": old_snapshot.vocabulary_size,
            "new_vocabulary_size": new_snapshot.vocabulary_size,
            "old_corpus_size": old_snapshot.corpus_size,
            "new_corpus_size": new_snapshot.corpus_size,
        }

        self._drift_events.append(event)

        # Keep only last 100 events
        if len(self._drift_events) > 100:
            self._drift_events = self._drift_events[-100:]

    def get_drift_history(self) -> List[Dict[str, Any]]:
        """Get history of drift events.

        Returns:
            List of drift event dictionaries
        """
        return self._drift_events.copy()

    def get_current_drift(self, embedding_generator: Any) -> Optional[DriftMetrics]:
        """Get current drift without triggering snapshot interval.

        Args:
            embedding_generator: EmbeddingGenerator instance

        Returns:
            DriftMetrics if snapshots available, None otherwise
        """
        if len(self.snapshots) < 2:
            return None

        # Compare last two snapshots
        old_snapshot = self.snapshots[-2]
        new_snapshot = self.snapshots[-1]

        return self.calculate_drift(old_snapshot, new_snapshot)

    def reset(self) -> None:
        """Reset monitor state."""
        self.snapshots.clear()
        self._drift_events.clear()
        self._last_snapshot_time = 0.0

        self._logger.info("vocabulary_drift_monitor_reset")

    def stats(self) -> Dict[str, Any]:
        """Get monitor statistics.

        Returns:
            Dictionary with monitor statistics
        """
        current_drift = None
        if len(self.snapshots) >= 2:
            current_drift = self.calculate_drift(self.snapshots[-2], self.snapshots[-1]).to_dict()

        return {
            "drift_threshold": self.drift_threshold,
            "snapshot_interval": self.snapshot_interval,
            "snapshots_count": len(self.snapshots),
            "drift_events_count": len(self._drift_events),
            "last_snapshot_time": self._last_snapshot_time,
            "current_drift": current_drift,
        }


# Global vocabulary drift monitor instance
_drift_monitor: Optional[VocabularyDriftMonitor] = None


def get_drift_monitor() -> VocabularyDriftMonitor:
    """Get global vocabulary drift monitor instance.

    Returns:
        Global VocabularyDriftMonitor instance
    """
    global _drift_monitor

    if _drift_monitor is None:
        _drift_monitor = VocabularyDriftMonitor()

    return _drift_monitor


def configure_drift_monitor(
    drift_threshold: float = 0.3, snapshot_interval: float = 300.0, max_snapshots: int = 100
) -> VocabularyDriftMonitor:
    """Configure global vocabulary drift monitor.

    Args:
        drift_threshold: Threshold for significant drift (0-1)
        snapshot_interval: Minimum time between snapshots (seconds)
        max_snapshots: Maximum number of snapshots to keep

    Returns:
        Configured VocabularyDriftMonitor instance
    """
    global _drift_monitor

    _drift_monitor = VocabularyDriftMonitor(
        drift_threshold=drift_threshold,
        snapshot_interval=snapshot_interval,
        max_snapshots=max_snapshots,
    )

    return _drift_monitor
