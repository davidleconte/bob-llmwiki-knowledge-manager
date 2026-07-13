"""
Core Functionality Tests for Phase 3 Validation Tools

Simplified test suite focusing on essential functionality that exists
in the current implementation. Tests core classes and methods without
requiring helper functions that haven't been implemented yet.
"""

import json
import pytest
import time
from pathlib import Path
from unittest.mock import Mock, patch
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from examples.bob_shell_session_tracker import (
    QueryRecord,
    BobShellSessionTracker,
    SessionSummary
)


class TestQueryRecordCore:
    """Test QueryRecord dataclass core functionality."""
    
    def test_query_record_creation(self):
        """Test creating a QueryRecord with all fields."""
        record = QueryRecord(
            query_id="q1",
            timestamp=time.time(),
            query_text="Test query",
            context_text="Test context",
            baseline_tokens=100,
            optimized_tokens=75,
            tokens_saved=25,
            savings_percent=25.0,
            cache_hit=False,
            optimization_applied=True,
            truncation_applied=False,
            latency_ms=5.0
        )
        
        assert record.query_id == "q1"
        assert record.query_text == "Test query"
        assert record.baseline_tokens == 100
        assert record.optimized_tokens == 75
        assert record.tokens_saved == 25
        assert record.savings_percent == 25.0
        assert record.cache_hit is False
        assert record.optimization_applied is True
    
    def test_query_record_savings_calculation(self):
        """Test that savings percentage is correctly stored."""
        record = QueryRecord(
            query_id="q1",
            timestamp=time.time(),
            query_text="Test",
            context_text="",
            baseline_tokens=1000,
            optimized_tokens=750,
            tokens_saved=250,
            savings_percent=25.0,
            cache_hit=False,
            optimization_applied=True,
            truncation_applied=False,
            latency_ms=5.0
        )
        
        # Verify savings calculation
        expected_savings = (250 / 1000) * 100
        assert record.savings_percent == pytest.approx(expected_savings, rel=0.01)


class TestSessionSummaryCore:
    """Test SessionSummary dataclass core functionality."""
    
    def test_session_summary_creation(self):
        """Test creating a SessionSummary."""
        queries = [
            QueryRecord(
                query_id=f"q{i}",
                timestamp=time.time(),
                query_text=f"Query {i}",
                context_text="",
                baseline_tokens=1000,
                optimized_tokens=750,
                tokens_saved=250,
                savings_percent=25.0,
                cache_hit=False,
                optimization_applied=True,
                truncation_applied=False,
                latency_ms=5.0
            )
            for i in range(5)
        ]
        
        summary = SessionSummary(
            session_id="test_001",
            mode="optimized",
            start_time=time.time(),
            end_time=time.time() + 100,
            duration_seconds=100.0,
            total_queries=5,
            total_baseline_tokens=5000,
            total_optimized_tokens=3750,
            total_tokens_saved=1250,
            overall_savings_percent=25.0,
            cache_hit_rate=0.0,
            optimization_rate=100.0,
            truncation_rate=0.0,
            avg_latency_ms=5.0,
            queries=queries
        )
        
        assert summary.session_id == "test_001"
        assert summary.mode == "optimized"
        assert summary.total_queries == 5
        assert summary.total_baseline_tokens == 5000
        assert summary.total_optimized_tokens == 3750
        assert summary.overall_savings_percent == 25.0


class TestBobShellSessionTrackerCore:
    """Test BobShellSessionTracker core functionality."""
    
    @pytest.fixture
    def temp_data_dir(self, tmp_path):
        """Provide temporary directory for session data."""
        data_dir = tmp_path / "sessions"
        data_dir.mkdir()
        return data_dir
    
    def test_tracker_initialization_baseline(self, temp_data_dir):
        """Test tracker initialization in baseline mode."""
        tracker = BobShellSessionTracker(
            session_id="test_001",
            mode="baseline",
            data_dir=temp_data_dir
        )
        
        assert tracker.session_id == "test_001"
        assert tracker.mode == "baseline"
        assert tracker.data_dir == temp_data_dir
    
    def test_tracker_initialization_optimized(self, temp_data_dir):
        """Test tracker initialization in optimized mode."""
        tracker = BobShellSessionTracker(
            session_id="test_002",
            mode="optimized",
            data_dir=temp_data_dir
        )
        
        assert tracker.session_id == "test_002"
        assert tracker.mode == "optimized"
    
    def test_invalid_mode_raises_error(self, temp_data_dir):
        """Test that invalid mode raises ValueError."""
        with pytest.raises(ValueError, match="Mode must be"):
            BobShellSessionTracker(
                session_id="test",
                mode="invalid",
                data_dir=temp_data_dir
            )
    
    def test_data_directory_creation(self, tmp_path):
        """Test that data directory is created if it doesn't exist."""
        non_existent_dir = tmp_path / "new_sessions"
        
        tracker = BobShellSessionTracker(
            session_id="test",
            mode="baseline",
            data_dir=non_existent_dir
        )
        
        assert non_existent_dir.exists()


class TestDataPersistence:
    """Test data persistence functionality."""
    
    @pytest.fixture
    def temp_data_dir(self, tmp_path):
        """Provide temporary directory for test data."""
        data_dir = tmp_path / "sessions"
        data_dir.mkdir()
        return data_dir
    
    def test_session_file_path(self, temp_data_dir):
        """Test that session file path is correctly constructed."""
        tracker = BobShellSessionTracker(
            session_id="test_001",
            mode="baseline",
            data_dir=temp_data_dir
        )
        
        expected_path = temp_data_dir / "test_001.json"
        assert tracker.session_file == expected_path
    
    def test_json_serialization(self):
        """Test that QueryRecord can be serialized to JSON."""
        record = QueryRecord(
            query_id="q1",
            timestamp=time.time(),
            query_text="Test",
            context_text="",
            baseline_tokens=100,
            optimized_tokens=75,
            tokens_saved=25,
            savings_percent=25.0,
            cache_hit=False,
            optimization_applied=True,
            truncation_applied=False,
            latency_ms=5.0
        )
        
        # Convert to dict (dataclass feature)
        from dataclasses import asdict
        record_dict = asdict(record)
        
        # Should be JSON serializable
        json_str = json.dumps(record_dict)
        assert isinstance(json_str, str)
        
        # Should be deserializable
        loaded_dict = json.loads(json_str)
        assert loaded_dict["query_id"] == "q1"
        assert loaded_dict["baseline_tokens"] == 100


class TestErrorHandling:
    """Test error handling in validation tools."""
    
    @pytest.fixture
    def temp_data_dir(self, tmp_path):
        """Provide temporary directory."""
        data_dir = tmp_path / "sessions"
        data_dir.mkdir()
        return data_dir
    
    def test_invalid_session_id(self, temp_data_dir):
        """Test handling of invalid session ID."""
        # Empty session ID should raise error
        with pytest.raises((ValueError, AssertionError)):
            BobShellSessionTracker(
                session_id="",
                mode="baseline",
                data_dir=temp_data_dir
            )
    
    def test_negative_token_counts(self):
        """Test that negative token counts are handled."""
        # Should raise error or handle gracefully
        with pytest.raises((ValueError, AssertionError)):
            QueryRecord(
                query_id="q1",
                timestamp=time.time(),
                query_text="Test",
                context_text="",
                baseline_tokens=-100,  # Invalid
                optimized_tokens=75,
                tokens_saved=25,
                savings_percent=25.0,
                cache_hit=False,
                optimization_applied=True,
                truncation_applied=False,
                latency_ms=5.0
            )


class TestIntegrationBasic:
    """Basic integration tests."""
    
    @pytest.fixture
    def temp_data_dir(self, tmp_path):
        """Provide temporary directory."""
        data_dir = tmp_path / "sessions"
        data_dir.mkdir()
        return data_dir
    
    def test_tracker_lifecycle(self, temp_data_dir):
        """Test complete tracker lifecycle: create, use, verify."""
        # Create tracker
        tracker = BobShellSessionTracker(
            session_id="lifecycle_test",
            mode="baseline",
            data_dir=temp_data_dir
        )
        
        # Verify initialization
        assert tracker.session_id == "lifecycle_test"
        assert tracker.mode == "baseline"
        assert tracker.data_dir.exists()
        
        # Verify session file path
        expected_file = temp_data_dir / "lifecycle_test.json"
        assert tracker.session_file == expected_file


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
