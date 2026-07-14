"""Tests for vocabulary drift monitoring."""

import time
from unittest.mock import Mock

import pytest

from src.monitoring.vocabulary_drift import (
    DriftMetrics,
    VocabularyDriftMonitor,
    VocabularySnapshot,
    configure_drift_monitor,
    get_drift_monitor,
)


class TestVocabularySnapshot:
    """Tests for VocabularySnapshot."""

    def test_create_snapshot(self):
        """Test creating a vocabulary snapshot."""
        vocab = {"word1", "word2", "word3"}
        snapshot = VocabularySnapshot(
            timestamp=time.time(),
            vocabulary=vocab,
            vocabulary_size=len(vocab),
            corpus_size=10,
            top_terms=["word1", "word2"]
        )

        assert snapshot.vocabulary_size == 3
        assert snapshot.corpus_size == 10
        assert len(snapshot.top_terms) == 2

    def test_snapshot_to_dict(self):
        """Test converting snapshot to dictionary."""
        vocab = {"word1", "word2"}
        snapshot = VocabularySnapshot(
            timestamp=123.45,
            vocabulary=vocab,
            vocabulary_size=2,
            corpus_size=5,
            top_terms=["word1", "word2"]
        )

        data = snapshot.to_dict()

        assert data["timestamp"] == 123.45
        assert data["vocabulary_size"] == 2
        assert data["corpus_size"] == 5
        assert data["top_terms"] == ["word1", "word2"]


class TestDriftMetrics:
    """Tests for DriftMetrics."""

    def test_create_drift_metrics(self):
        """Test creating drift metrics."""
        metrics = DriftMetrics(
            new_terms=5,
            removed_terms=3,
            total_change=8,
            change_rate=0.2,
            drift_score=0.25
        )

        assert metrics.new_terms == 5
        assert metrics.removed_terms == 3
        assert metrics.total_change == 8
        assert metrics.change_rate == 0.2
        assert metrics.drift_score == 0.25

    def test_metrics_to_dict(self):
        """Test converting metrics to dictionary."""
        metrics = DriftMetrics(
            new_terms=5,
            removed_terms=3,
            total_change=8,
            change_rate=0.2,
            drift_score=0.25
        )

        data = metrics.to_dict()

        assert data["new_terms"] == 5
        assert data["removed_terms"] == 3
        assert data["total_change"] == 8
        assert data["change_rate"] == 0.2
        assert data["drift_score"] == 0.25


class TestVocabularyDriftMonitor:
    """Tests for VocabularyDriftMonitor."""

    def test_create_monitor(self):
        """Test creating drift monitor."""
        monitor = VocabularyDriftMonitor(
            drift_threshold=0.3,
            snapshot_interval=60.0,
            max_snapshots=50
        )

        assert monitor.drift_threshold == 0.3
        assert monitor.snapshot_interval == 60.0
        assert monitor.max_snapshots == 50
        assert len(monitor.snapshots) == 0

    def test_invalid_threshold(self):
        """Test that invalid threshold raises error."""
        with pytest.raises(ValueError):
            VocabularyDriftMonitor(drift_threshold=1.5)

        with pytest.raises(ValueError):
            VocabularyDriftMonitor(drift_threshold=-0.1)

    def test_take_snapshot(self):
        """Test taking a vocabulary snapshot."""
        monitor = VocabularyDriftMonitor()

        # Mock embedding generator
        mock_gen = Mock()
        mock_gen.corpus = ["doc1", "doc2", "doc3"]
        mock_gen.vectorizer = Mock()
        mock_gen.vectorizer.vocabulary_ = {"word1": 0, "word2": 1, "word3": 2}
        mock_gen.vectorizer.get_feature_names_out = Mock(return_value=["word1", "word2", "word3"])

        snapshot = monitor.take_snapshot(mock_gen)

        assert snapshot.vocabulary_size == 3
        assert snapshot.corpus_size == 3
        assert len(monitor.snapshots) == 1

    def test_snapshot_interval_respected(self):
        """Test that snapshot interval is respected."""
        monitor = VocabularyDriftMonitor(snapshot_interval=1.0)

        mock_gen = Mock()
        mock_gen.corpus = ["doc1"]
        mock_gen.vectorizer = Mock()
        mock_gen.vectorizer.vocabulary_ = {"word1": 0}

        # Take first snapshot
        snapshot1 = monitor.take_snapshot(mock_gen)

        # Try to take another immediately (should return same snapshot)
        snapshot2 = monitor.take_snapshot(mock_gen)

        assert snapshot1 is snapshot2
        assert len(monitor.snapshots) == 1

        # Wait for interval
        time.sleep(1.1)

        # Now should take new snapshot
        snapshot3 = monitor.take_snapshot(mock_gen)

        assert snapshot3 is not snapshot1
        assert len(monitor.snapshots) == 2

    def test_calculate_drift_no_change(self):
        """Test drift calculation with no vocabulary change."""
        monitor = VocabularyDriftMonitor()

        vocab = {"word1", "word2", "word3"}
        old_snapshot = VocabularySnapshot(
            timestamp=100.0,
            vocabulary=vocab.copy(),
            vocabulary_size=3,
            corpus_size=10
        )
        new_snapshot = VocabularySnapshot(
            timestamp=200.0,
            vocabulary=vocab.copy(),
            vocabulary_size=3,
            corpus_size=10
        )

        metrics = monitor.calculate_drift(old_snapshot, new_snapshot)

        assert metrics.new_terms == 0
        assert metrics.removed_terms == 0
        assert metrics.total_change == 0
        assert metrics.change_rate == 0.0

    def test_calculate_drift_with_changes(self):
        """Test drift calculation with vocabulary changes."""
        monitor = VocabularyDriftMonitor()

        old_vocab = {"word1", "word2", "word3"}
        new_vocab = {"word1", "word2", "word4", "word5"}  # word3 removed, word4/5 added

        old_snapshot = VocabularySnapshot(
            timestamp=100.0,
            vocabulary=old_vocab,
            vocabulary_size=3,
            corpus_size=10
        )
        new_snapshot = VocabularySnapshot(
            timestamp=200.0,
            vocabulary=new_vocab,
            vocabulary_size=4,
            corpus_size=12
        )

        metrics = monitor.calculate_drift(old_snapshot, new_snapshot)

        assert metrics.new_terms == 2  # word4, word5
        assert metrics.removed_terms == 1  # word3
        assert metrics.total_change == 3
        assert metrics.change_rate == 3 / 3  # 3 changes / 3 old terms = 1.0

    def test_check_drift_insufficient_snapshots(self):
        """Test drift check with insufficient snapshots."""
        monitor = VocabularyDriftMonitor()

        mock_gen = Mock()
        mock_gen.corpus = ["doc1"]
        mock_gen.vectorizer = Mock()
        mock_gen.vectorizer.vocabulary_ = {"word1": 0}

        # First snapshot - should return None (need 2 snapshots)
        result = monitor.check_drift(mock_gen)
        assert result is None

    def test_check_drift_below_threshold(self):
        """Test drift check below threshold."""
        monitor = VocabularyDriftMonitor(
            drift_threshold=0.5,
            snapshot_interval=0.1
        )

        # First snapshot
        mock_gen = Mock()
        mock_gen.corpus = ["doc1", "doc2"]
        mock_gen.vectorizer = Mock()
        mock_gen.vectorizer.vocabulary_ = {"word1": 0, "word2": 1}

        monitor.take_snapshot(mock_gen)
        time.sleep(0.15)

        # Second snapshot with small change
        mock_gen.vocabulary_ = {"word1": 0, "word2": 1, "word3": 2}
        mock_gen.corpus = ["doc1", "doc2", "doc3"]

        result = monitor.check_drift(mock_gen)

        # Small change should not trigger drift
        assert result is None

    def test_check_drift_above_threshold(self):
        """Test drift check above threshold."""
        monitor = VocabularyDriftMonitor(
            drift_threshold=0.3,
            snapshot_interval=0.1
        )

        # First snapshot
        mock_gen = Mock()
        mock_gen.corpus = ["doc1", "doc2"]
        mock_gen.vectorizer = Mock()
        mock_gen.vectorizer.vocabulary_ = {"word1": 0, "word2": 1}

        monitor.take_snapshot(mock_gen)
        time.sleep(0.15)

        # Second snapshot with large change
        mock_gen.vectorizer.vocabulary_ = {
            "word3": 0, "word4": 1, "word5": 2, "word6": 3
        }
        mock_gen.corpus = ["doc3", "doc4", "doc5", "doc6"]

        result = monitor.check_drift(mock_gen)

        # Large change should trigger drift
        assert result is not None
        assert result.drift_score >= monitor.drift_threshold

    def test_drift_event_recording(self):
        """Test that drift events are recorded."""
        monitor = VocabularyDriftMonitor(
            drift_threshold=0.3,
            snapshot_interval=0.1
        )

        # Create significant drift
        mock_gen = Mock()
        mock_gen.corpus = ["doc1"]
        mock_gen.vectorizer = Mock()
        mock_gen.vectorizer.vocabulary_ = {"word1": 0}

        monitor.take_snapshot(mock_gen)
        time.sleep(0.15)

        mock_gen.vectorizer.vocabulary_ = {"word2": 0, "word3": 1, "word4": 2}
        mock_gen.corpus = ["doc2", "doc3", "doc4"]

        monitor.check_drift(mock_gen)

        # Check drift event was recorded
        history = monitor.get_drift_history()
        assert len(history) > 0
        assert "metrics" in history[0]
        assert "timestamp" in history[0]

    def test_get_current_drift(self):
        """Test getting current drift without new snapshot."""
        monitor = VocabularyDriftMonitor(snapshot_interval=0.1)

        # Take two snapshots
        mock_gen = Mock()
        mock_gen.corpus = ["doc1"]
        mock_gen.vectorizer = Mock()
        mock_gen.vectorizer.vocabulary_ = {"word1": 0}

        monitor.take_snapshot(mock_gen)
        time.sleep(0.15)

        mock_gen.vectorizer.vocabulary_ = {"word1": 0, "word2": 1}
        monitor.take_snapshot(mock_gen)

        # Get current drift
        drift = monitor.get_current_drift(mock_gen)

        assert drift is not None
        assert drift.new_terms == 1

    def test_reset(self):
        """Test resetting monitor state."""
        monitor = VocabularyDriftMonitor()

        # Add some data
        mock_gen = Mock()
        mock_gen.corpus = ["doc1"]
        mock_gen.vectorizer = Mock()
        mock_gen.vectorizer.vocabulary_ = {"word1": 0}

        monitor.take_snapshot(mock_gen)

        # Reset
        monitor.reset()

        assert len(monitor.snapshots) == 0
        assert len(monitor._drift_events) == 0
        assert monitor._last_snapshot_time == 0.0

    def test_stats(self):
        """Test getting monitor statistics."""
        monitor = VocabularyDriftMonitor()

        stats = monitor.stats()

        assert "drift_threshold" in stats
        assert "snapshot_interval" in stats
        assert "snapshots_count" in stats
        assert "drift_events_count" in stats
        assert stats["snapshots_count"] == 0

    def test_max_snapshots_limit(self):
        """Test that max snapshots limit is enforced."""
        monitor = VocabularyDriftMonitor(
            max_snapshots=5,
            snapshot_interval=0.01
        )

        mock_gen = Mock()
        mock_gen.corpus = ["doc1"]
        mock_gen.vectorizer = Mock()
        mock_gen.vectorizer.vocabulary_ = {"word1": 0}

        # Take more than max snapshots
        for i in range(10):
            mock_gen.corpus = [f"doc{i}"]
            monitor.take_snapshot(mock_gen)
            time.sleep(0.02)

        # Should only keep last 5
        assert len(monitor.snapshots) == 5


class TestGlobalDriftMonitor:
    """Tests for global drift monitor."""

    def test_get_drift_monitor_singleton(self):
        """Test that get_drift_monitor returns singleton."""
        monitor1 = get_drift_monitor()
        monitor2 = get_drift_monitor()

        assert monitor1 is monitor2

    def test_configure_drift_monitor(self):
        """Test configuring global drift monitor."""
        monitor = configure_drift_monitor(
            drift_threshold=0.4,
            snapshot_interval=120.0,
            max_snapshots=200
        )

        assert monitor.drift_threshold == 0.4
        assert monitor.snapshot_interval == 120.0
        assert monitor.max_snapshots == 200


class TestDriftScoreCalculation:
    """Tests for drift score calculation logic."""

    def test_drift_score_vocabulary_only(self):
        """Test drift score with vocabulary change only."""
        monitor = VocabularyDriftMonitor()

        old_vocab = {"word1", "word2", "word3", "word4"}
        new_vocab = {"word1", "word2", "word5", "word6"}  # 50% change

        old_snapshot = VocabularySnapshot(
            timestamp=100.0,
            vocabulary=old_vocab,
            vocabulary_size=4,
            corpus_size=10
        )
        new_snapshot = VocabularySnapshot(
            timestamp=200.0,
            vocabulary=new_vocab,
            vocabulary_size=4,
            corpus_size=10  # No corpus change
        )

        metrics = monitor.calculate_drift(old_snapshot, new_snapshot)

        # Drift score should be primarily from vocabulary change
        # change_rate = 4/4 = 1.0
        # corpus_growth_rate = 0
        # drift_score = 0.7 * 1.0 + 0.3 * 0 = 0.7
        assert metrics.drift_score == pytest.approx(0.7, rel=0.01)

    def test_drift_score_corpus_growth(self):
        """Test drift score with corpus growth."""
        monitor = VocabularyDriftMonitor()

        old_vocab = {"word1", "word2"}
        new_vocab = {"word1", "word2", "word3"}  # Small vocab change

        old_snapshot = VocabularySnapshot(
            timestamp=100.0,
            vocabulary=old_vocab,
            vocabulary_size=2,
            corpus_size=10
        )
        new_snapshot = VocabularySnapshot(
            timestamp=200.0,
            vocabulary=new_vocab,
            vocabulary_size=3,
            corpus_size=20  # 100% corpus growth
        )

        metrics = monitor.calculate_drift(old_snapshot, new_snapshot)

        # change_rate = 1/2 = 0.5
        # corpus_growth_rate = 10/10 = 1.0
        # drift_score = 0.7 * 0.5 + 0.3 * 1.0 = 0.35 + 0.3 = 0.65
        assert metrics.drift_score == pytest.approx(0.65, rel=0.01)
