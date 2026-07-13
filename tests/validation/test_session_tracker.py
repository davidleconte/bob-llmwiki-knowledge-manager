"""
Tests for Bob Shell Session Tracker

Tests the session tracking functionality used for Phase 3 validation.
"""

import json
import pytest
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from examples.bob_shell_session_tracker import (
    QueryRecord,
    BobShellSessionTracker,
    SessionSummary
)


class TestQueryRecord:
    """Test QueryRecord dataclass."""
    
    def test_query_record_creation(self):
        """Test creating a QueryRecord."""
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
    
    def test_query_record_savings_calculation(self):
        """Test savings percentage calculation."""
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


class TestBobShellSessionTracker:
    """Test BobShellSessionTracker class."""
    
    @pytest.fixture
    def temp_session_dir(self, tmp_path):
        """Provide temporary directory for session files."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir()
        return session_dir
    
    @pytest.fixture
    def mock_optimizer(self):
        """Provide mock PromptOptimizer."""
        optimizer = Mock()
        optimizer.optimize.return_value = {
            "optimized_prompt": "optimized text",
            "original_tokens": 100,
            "optimized_tokens": 75,
            "savings": 25,
            "savings_percent": 25.0
        }
        return optimizer
    
    @pytest.fixture
    def mock_cache(self):
        """Provide mock MultiLevelCache."""
        cache = Mock()
        cache.get.return_value = None  # Default: cache miss
        return cache
    
    @pytest.fixture
    def mock_token_counter(self):
        """Provide mock TokenCounter."""
        counter = Mock()
        counter.count_tokens.return_value = 100
        return counter
    
    def test_session_tracker_initialization_baseline(self, temp_session_dir):
        """Test BobShellSessionTracker initialization in baseline mode."""
        with patch('examples.bob_shell_session_tracker.Path') as mock_path:
            mock_path.return_value = temp_session_dir
            
            tracker = BobShellBobShellSessionTracker(
                mode="baseline",
                session_id="test_001"
            )
            
            assert tracker.mode == "baseline"
            assert tracker.session_id == "test_001"
            assert tracker.queries == []
            assert tracker.start_time > 0
    
    def test_session_tracker_initialization_optimized(self, temp_session_dir):
        """Test BobShellSessionTracker initialization in optimized mode."""
        with patch('examples.bob_shell_session_tracker.Path') as mock_path:
            mock_path.return_value = temp_session_dir
            
            tracker = BobShellSessionTracker(
                mode="optimized",
                session_id="test_002"
            )
            
            assert tracker.mode == "optimized"
            assert tracker.session_id == "test_002"
    
    def test_invalid_mode_raises_error(self, temp_session_dir):
        """Test that invalid mode raises ValueError."""
        with patch('examples.bob_shell_session_tracker.Path') as mock_path:
            mock_path.return_value = temp_session_dir
            
            with pytest.raises(ValueError, match="Mode must be 'baseline' or 'optimized'"):
                BobShellSessionTracker(mode="invalid", session_id="test")
    
    def test_track_query_baseline_mode(self, temp_session_dir, mock_token_counter):
        """Test tracking a query in baseline mode."""
        with patch('examples.bob_shell_session_tracker.Path') as mock_path:
            mock_path.return_value = temp_session_dir
            
            with patch('examples.bob_shell_session_tracker.TokenCounter', return_value=mock_token_counter):
                tracker = BobShellBobShellSessionTracker(mode="baseline", session_id="test")
                
                tracker.track_query(
                    query_text="Test query",
                    context_text="Test context",
                    response_text="Test response"
                )
                
                assert len(tracker.queries) == 1
                query = tracker.queries[0]
                assert query.query_text == "Test query"
                assert query.baseline_tokens > 0
                assert query.optimized_tokens == query.baseline_tokens  # No optimization in baseline
                assert query.tokens_saved == 0
    
    def test_track_query_optimized_mode(self, temp_session_dir, mock_optimizer, mock_cache, mock_token_counter):
        """Test tracking a query in optimized mode."""
        with patch('examples.bob_shell_session_tracker.Path') as mock_path:
            mock_path.return_value = temp_session_dir
            
            with patch('examples.bob_shell_session_tracker.TokenCounter', return_value=mock_token_counter):
                with patch('examples.bob_shell_session_tracker.PromptOptimizer', return_value=mock_optimizer):
                    with patch('examples.bob_shell_session_tracker.MultiLevelCache', return_value=mock_cache):
                        tracker = BobShellSessionTracker(mode="optimized", session_id="test")
                        
                        tracker.track_query(
                            query_text="Test query",
                            context_text="Test context",
                            response_text="Test response"
                        )
                        
                        assert len(tracker.queries) == 1
                        query = tracker.queries[0]
                        assert query.optimization_applied is True
                        assert query.tokens_saved > 0
    
    def test_cache_hit_tracking(self, temp_session_dir, mock_cache, mock_token_counter):
        """Test that cache hits are tracked correctly."""
        mock_cache.get.return_value = "cached response"  # Cache hit
        
        with patch('examples.bob_shell_session_tracker.Path') as mock_path:
            mock_path.return_value = temp_session_dir
            
            with patch('examples.bob_shell_session_tracker.TokenCounter', return_value=mock_token_counter):
                with patch('examples.bob_shell_session_tracker.MultiLevelCache', return_value=mock_cache):
                    tracker = BobShellSessionTracker(mode="optimized", session_id="test")
                    
                    tracker.track_query(
                        query_text="Test query",
                        context_text="",
                        response_text="Test response"
                    )
                    
                    query = tracker.queries[0]
                    assert query.cache_hit is True
    
    def test_session_summary_calculation(self, temp_session_dir, mock_token_counter):
        """Test session summary statistics calculation."""
        with patch('examples.bob_shell_session_tracker.Path') as mock_path:
            mock_path.return_value = temp_session_dir
            
            with patch('examples.bob_shell_session_tracker.TokenCounter', return_value=mock_token_counter):
                tracker = BobShellSessionTracker(mode="baseline", session_id="test")
                
                # Add multiple queries
                for i in range(5):
                    tracker.track_query(
                        query_text=f"Query {i}",
                        context_text="",
                        response_text="Response"
                    )
                
                summary = tracker.get_summary()
                
                assert summary["total_queries"] == 5
                assert summary["total_baseline_tokens"] > 0
                assert "avg_tokens_per_query" in summary
    
    def test_save_session_data(self, temp_session_dir, mock_token_counter):
        """Test saving session data to file."""
        session_file = temp_session_dir / "test_session.json"
        
        with patch('examples.bob_shell_session_tracker.Path') as mock_path:
            mock_path.return_value = temp_session_dir
            
            with patch('examples.bob_shell_session_tracker.TokenCounter', return_value=mock_token_counter):
                tracker = BobShellSessionTracker(mode="baseline", session_id="test_session")
                
                tracker.track_query(
                    query_text="Test query",
                    context_text="",
                    response_text="Response"
                )
                
                # Mock the save method to write to our temp file
                with patch.object(tracker, 'session_file', session_file):
                    tracker.save()
                    
                    assert session_file.exists()
                    
                    # Verify file content
                    with open(session_file) as f:
                        data = json.load(f)
                        assert data["session_id"] == "test_session"
                        assert data["mode"] == "baseline"
                        assert len(data["queries"]) == 1
    
    def test_load_session_data(self, temp_session_dir):
        """Test loading session data from file."""
        session_file = temp_session_dir / "test_session.json"
        
        # Create mock session data
        session_data = {
            "session_id": "test_session",
            "mode": "baseline",
            "start_time": time.time(),
            "end_time": time.time() + 100,
            "queries": [
                {
                    "query_id": "q1",
                    "timestamp": time.time(),
                    "query_text": "Test",
                    "context_text": "",
                    "baseline_tokens": 100,
                    "optimized_tokens": 100,
                    "tokens_saved": 0,
                    "savings_percent": 0.0,
                    "cache_hit": False,
                    "optimization_applied": False,
                    "truncation_applied": False,
                    "latency_ms": 0.0
                }
            ]
        }
        
        with open(session_file, 'w') as f:
            json.dump(session_data, f)
        
        with patch('examples.bob_shell_session_tracker.Path') as mock_path:
            mock_path.return_value = temp_session_dir
            
            tracker = BobShellSessionTracker.load(session_file)
            
            assert tracker.session_id == "test_session"
            assert tracker.mode == "baseline"
            assert len(tracker.queries) == 1
    
    def test_missing_session_file_handling(self, temp_session_dir):
        """Test handling of missing session file."""
        missing_file = temp_session_dir / "nonexistent.json"
        
        with pytest.raises(FileNotFoundError):
            BobShellSessionTracker.load(missing_file)
    
    def test_corrupted_session_file_handling(self, temp_session_dir):
        """Test handling of corrupted session file."""
        corrupted_file = temp_session_dir / "corrupted.json"
        
        with open(corrupted_file, 'w') as f:
            f.write("{ invalid json }")
        
        with pytest.raises(json.JSONDecodeError):
            BobShellSessionTracker.load(corrupted_file)
    
    def test_latency_measurement(self, temp_session_dir, mock_token_counter):
        """Test that latency is measured for optimized queries."""
        with patch('examples.bob_shell_session_tracker.Path') as mock_path:
            mock_path.return_value = temp_session_dir
            
            with patch('examples.bob_shell_session_tracker.TokenCounter', return_value=mock_token_counter):
                tracker = BobShellSessionTracker(mode="optimized", session_id="test")
                
                tracker.track_query(
                    query_text="Test query",
                    context_text="",
                    response_text="Response"
                )
                
                query = tracker.queries[0]
                assert query.latency_ms >= 0  # Latency should be measured


class TestSessionAnalyzer:
    """Test SessionAnalyzer class."""
    
    @pytest.fixture
    def mock_sessions(self):
        """Provide mock session data."""
        baseline_session = Mock()
        baseline_session.session_id = "baseline_001"
        baseline_session.mode = "baseline"
        baseline_session.queries = [
            Mock(
                baseline_tokens=1000,
                optimized_tokens=1000,
                tokens_saved=0,
                savings_percent=0.0,
                cache_hit=False,
                optimization_applied=False
            )
            for _ in range(10)
        ]
        
        optimized_session = Mock()
        optimized_session.session_id = "optimized_001"
        optimized_session.mode = "optimized"
        optimized_session.queries = [
            Mock(
                baseline_tokens=1000,
                optimized_tokens=750,
                tokens_saved=250,
                savings_percent=25.0,
                cache_hit=True if i % 3 == 0 else False,
                optimization_applied=True
            )
            for i in range(10)
        ]
        
        return [baseline_session, optimized_session]
    
    def test_analyzer_initialization(self, mock_sessions):
        """Test SessionAnalyzer initialization."""
        analyzer = SessionAnalyzer(mock_sessions)
        
        assert len(analyzer.sessions) == 2
        assert analyzer.baseline_sessions is not None
        assert analyzer.optimized_sessions is not None
    
    def test_calculate_aggregate_stats(self, mock_sessions):
        """Test aggregate statistics calculation."""
        analyzer = SessionAnalyzer(mock_sessions)
        stats = analyzer.calculate_aggregate_stats()
        
        assert "total_queries" in stats
        assert "total_baseline_tokens" in stats
        assert "total_optimized_tokens" in stats
        assert "total_tokens_saved" in stats
        assert "overall_savings_percent" in stats
    
    def test_token_reduction_calculation(self, mock_sessions):
        """Test token reduction percentage calculation."""
        analyzer = SessionAnalyzer(mock_sessions)
        stats = analyzer.calculate_aggregate_stats()
        
        # Optimized session should show 25% reduction
        assert stats["overall_savings_percent"] > 0
    
    def test_cache_effectiveness_calculation(self, mock_sessions):
        """Test cache effectiveness metrics."""
        analyzer = SessionAnalyzer(mock_sessions)
        stats = analyzer.calculate_aggregate_stats()
        
        assert "cache_hit_rate" in stats
        assert stats["cache_hit_rate"] >= 0
        assert stats["cache_hit_rate"] <= 100
    
    def test_empty_sessions_handling(self):
        """Test handling of empty session list."""
        analyzer = SessionAnalyzer([])
        stats = analyzer.calculate_aggregate_stats()
        
        assert stats["total_queries"] == 0
        assert stats["overall_savings_percent"] == 0.0
    
    def test_comparison_analysis(self, mock_sessions):
        """Test baseline vs optimized comparison."""
        analyzer = SessionAnalyzer(mock_sessions)
        comparison = analyzer.compare_baseline_vs_optimized()
        
        assert "baseline_avg_tokens" in comparison
        assert "optimized_avg_tokens" in comparison
        assert "improvement_percent" in comparison
        assert comparison["improvement_percent"] > 0


class TestIntegration:
    """Integration tests for complete workflows."""
    
    @pytest.fixture
    def temp_session_dir(self, tmp_path):
        """Provide temporary directory for session files."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir()
        return session_dir
    
    def test_complete_baseline_workflow(self, temp_session_dir):
        """Test complete baseline session workflow."""
        with patch('examples.bob_shell_session_tracker.Path') as mock_path:
            mock_path.return_value = temp_session_dir
            
            # Create session
            tracker = BobShellSessionTracker(mode="baseline", session_id="integration_test")
            
            # Add queries
            for i in range(5):
                tracker.track_query(
                    query_text=f"Query {i}",
                    context_text=f"Context {i}",
                    response_text=f"Response {i}"
                )
            
            # Get summary
            summary = tracker.get_summary()
            assert summary["total_queries"] == 5
            
            # Save session
            session_file = temp_session_dir / "integration_test.json"
            with patch.object(tracker, 'session_file', session_file):
                tracker.save()
                assert session_file.exists()
            
            # Load session
            loaded_tracker = BobShellSessionTracker.load(session_file)
            assert loaded_tracker.session_id == "integration_test"
            assert len(loaded_tracker.queries) == 5


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
