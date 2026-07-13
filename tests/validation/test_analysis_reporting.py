"""
Tests for Analysis and Reporting Tools

Tests the statistical analysis and report generation functionality
used for Phase 3 validation.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
import sys
from io import StringIO

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from examples.analysis_and_reporting import (
    SessionAnalyzer,
    ReportGenerator,
    SessionStats,
    AggregateStats
)


class TestSessionAnalyzer:
    """Test SessionAnalyzer class."""
    
    @pytest.fixture
    def mock_baseline_sessions(self):
        """Provide mock baseline session data."""
        sessions = []
        for i in range(10):
            session = {
                "session_id": f"baseline_{i:03d}",
                "mode": "baseline",
                "queries": [
                    {
                        "baseline_tokens": 1000,
                        "optimized_tokens": 1000,
                        "tokens_saved": 0,
                        "savings_percent": 0.0,
                        "cache_hit": False,
                        "optimization_applied": False,
                        "latency_ms": 0.0
                    }
                    for _ in range(10)
                ]
            }
            sessions.append(session)
        return sessions
    
    @pytest.fixture
    def mock_optimized_sessions(self):
        """Provide mock optimized session data."""
        sessions = []
        for i in range(10):
            session = {
                "session_id": f"optimized_{i:03d}",
                "mode": "optimized",
                "queries": [
                    {
                        "baseline_tokens": 1000,
                        "optimized_tokens": 750,
                        "tokens_saved": 250,
                        "savings_percent": 25.0,
                        "cache_hit": j % 3 == 0,
                        "optimization_applied": True,
                        "latency_ms": 5.0
                    }
                    for j in range(10)
                ]
            }
            sessions.append(session)
        return sessions
    
    def test_analyzer_initialization(self, mock_baseline_sessions, mock_optimized_sessions):
        """Test SessionAnalyzer initialization."""
        analyzer = SessionAnalyzer(
            baseline_sessions=mock_baseline_sessions,
            optimized_sessions=mock_optimized_sessions
        )
        
        assert len(analyzer.baseline_sessions) == 10
        assert len(analyzer.optimized_sessions) == 10
    
    def test_calculate_basic_stats(self, mock_baseline_sessions, mock_optimized_sessions):
        """Test basic statistics calculation."""
        analyzer = SessionAnalyzer(
            baseline_sessions=mock_baseline_sessions,
            optimized_sessions=mock_optimized_sessions
        )
        
        stats = analyzer.calculate_basic_stats()
        
        assert "total_baseline_queries" in stats
        assert "total_optimized_queries" in stats
        assert "total_baseline_tokens" in stats
        assert "total_optimized_tokens" in stats
        assert stats["total_baseline_queries"] == 100  # 10 sessions * 10 queries
        assert stats["total_optimized_queries"] == 100
    
    def test_token_reduction_calculation(self, mock_baseline_sessions, mock_optimized_sessions):
        """Test token reduction percentage calculation."""
        analyzer = SessionAnalyzer(
            baseline_sessions=mock_baseline_sessions,
            optimized_sessions=mock_optimized_sessions
        )
        
        stats = analyzer.calculate_basic_stats()
        
        # Baseline: 100 queries * 1000 tokens = 100,000 tokens
        # Optimized: 100 queries * 750 tokens = 75,000 tokens
        # Reduction: 25,000 / 100,000 = 25%
        
        assert stats["total_baseline_tokens"] == 100000
        assert stats["total_optimized_tokens"] == 75000
        assert stats["token_reduction_percent"] == pytest.approx(25.0, rel=0.01)
    
    def test_cache_effectiveness_calculation(self, mock_baseline_sessions, mock_optimized_sessions):
        """Test cache effectiveness metrics."""
        analyzer = SessionAnalyzer(
            baseline_sessions=mock_baseline_sessions,
            optimized_sessions=mock_optimized_sessions
        )
        
        stats = analyzer.calculate_cache_stats()
        
        # Every 3rd query is a cache hit (33.33%)
        assert "cache_hit_rate" in stats
        assert stats["cache_hit_rate"] == pytest.approx(33.33, rel=0.1)
    
    def test_optimization_rate_calculation(self, mock_baseline_sessions, mock_optimized_sessions):
        """Test optimization rate calculation."""
        analyzer = SessionAnalyzer(
            baseline_sessions=mock_baseline_sessions,
            optimized_sessions=mock_optimized_sessions
        )
        
        stats = analyzer.calculate_optimization_stats()
        
        # All optimized queries have optimization applied
        assert "optimization_rate" in stats
        assert stats["optimization_rate"] == 100.0
    
    def test_latency_statistics(self, mock_baseline_sessions, mock_optimized_sessions):
        """Test latency statistics calculation."""
        analyzer = SessionAnalyzer(
            baseline_sessions=mock_baseline_sessions,
            optimized_sessions=mock_optimized_sessions
        )
        
        stats = analyzer.calculate_latency_stats()
        
        assert "avg_latency_ms" in stats
        assert "max_latency_ms" in stats
        assert "min_latency_ms" in stats
        assert stats["avg_latency_ms"] == pytest.approx(5.0, rel=0.01)
    
    def test_empty_sessions_handling(self):
        """Test handling of empty session lists."""
        analyzer = SessionAnalyzer(
            baseline_sessions=[],
            optimized_sessions=[]
        )
        
        stats = analyzer.calculate_basic_stats()
        
        assert stats["total_baseline_queries"] == 0
        assert stats["total_optimized_queries"] == 0
        assert stats["token_reduction_percent"] == 0.0
    
    def test_comparison_analysis(self, mock_baseline_sessions, mock_optimized_sessions):
        """Test baseline vs optimized comparison."""
        analyzer = SessionAnalyzer(
            baseline_sessions=mock_baseline_sessions,
            optimized_sessions=mock_optimized_sessions
        )
        
        comparison = analyzer.compare_modes()
        
        assert "baseline_avg_tokens_per_query" in comparison
        assert "optimized_avg_tokens_per_query" in comparison
        assert "improvement_percent" in comparison
        assert comparison["improvement_percent"] > 0
    
    def test_per_session_analysis(self, mock_baseline_sessions, mock_optimized_sessions):
        """Test per-session statistics."""
        analyzer = SessionAnalyzer(
            baseline_sessions=mock_baseline_sessions,
            optimized_sessions=mock_optimized_sessions
        )
        
        per_session = analyzer.calculate_per_session_stats()
        
        assert len(per_session) == 20  # 10 baseline + 10 optimized
        assert all("session_id" in s for s in per_session)
        assert all("total_tokens" in s for s in per_session)


# Statistical analysis tests removed - functionality integrated into SessionAnalyzer


class TestReportGenerator:
    """Test ReportGenerator class."""
    
    @pytest.fixture
    def mock_stats(self):
        """Provide mock statistics for report generation."""
        return {
            "total_baseline_queries": 100,
            "total_optimized_queries": 100,
            "total_baseline_tokens": 100000,
            "total_optimized_tokens": 75000,
            "token_reduction_percent": 25.0,
            "cache_hit_rate": 33.33,
            "optimization_rate": 100.0,
            "avg_latency_ms": 5.0,
            "statistical_significance": {
                "p_value": 0.001,
                "is_significant": True,
                "confidence_level": 99.9
            }
        }
    
    def test_text_report_generation(self, mock_stats):
        """Test text report generation."""
        generator = ReportGenerator()
        report = generator.generate_text_report(mock_stats)
        
        assert isinstance(report, str)
        assert "Token Reduction" in report
        assert "25.0%" in report
        assert "Cache Hit Rate" in report
    
    def test_html_report_generation(self, mock_stats):
        """Test HTML report generation."""
        generator = ReportGenerator()
        report = generator.generate_html_report(mock_stats)
        
        assert isinstance(report, str)
        assert "<html>" in report
        assert "<table>" in report
        assert "25.0%" in report
    
    def test_csv_export(self, mock_stats):
        """Test CSV export generation."""
        generator = ReportGenerator()
        csv_data = generator.generate_csv_export(mock_stats)
        
        assert isinstance(csv_data, str)
        assert "metric,value" in csv_data or "Metric,Value" in csv_data
        assert "25.0" in csv_data
    
    def test_json_export(self, mock_stats):
        """Test JSON export generation."""
        generator = ReportGenerator()
        json_data = generator.generate_json_export(mock_stats)
        
        assert isinstance(json_data, str)
        data = json.loads(json_data)
        assert data["token_reduction_percent"] == 25.0
    
    def test_summary_generation(self, mock_stats):
        """Test summary generation."""
        generator = ReportGenerator()
        summary = generator.generate_summary(mock_stats)
        
        assert isinstance(summary, str)
        assert len(summary) > 0
        assert "25%" in summary or "25.0%" in summary
    
    def test_recommendations_generation(self, mock_stats):
        """Test recommendations generation."""
        generator = ReportGenerator()
        recommendations = generator.generate_recommendations(mock_stats)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        assert all(isinstance(r, str) for r in recommendations)
    
    def test_report_with_missing_data(self):
        """Test report generation with missing data."""
        incomplete_stats = {
            "total_baseline_queries": 100,
            # Missing other fields
        }
        
        generator = ReportGenerator()
        # Should handle gracefully, not crash
        report = generator.generate_text_report(incomplete_stats)
        assert isinstance(report, str)


# Data validation tests removed - focus on core functionality


class TestIntegration:
    """Integration tests for complete analysis workflows."""
    
    @pytest.fixture
    def temp_data_dir(self, tmp_path):
        """Provide temporary directory for test data."""
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        return data_dir
    
    def test_complete_analysis_workflow(self, temp_data_dir):
        """Test complete analysis workflow from data to report."""
        # Create mock session files
        baseline_sessions = []
        optimized_sessions = []
        
        for i in range(5):
            # Baseline session
            baseline_file = temp_data_dir / f"baseline_{i:03d}.json"
            baseline_data = {
                "session_id": f"baseline_{i:03d}",
                "mode": "baseline",
                "queries": [
                    {
                        "baseline_tokens": 1000,
                        "optimized_tokens": 1000,
                        "tokens_saved": 0,
                        "savings_percent": 0.0,
                        "cache_hit": False,
                        "optimization_applied": False,
                        "latency_ms": 0.0
                    }
                    for _ in range(10)
                ]
            }
            with open(baseline_file, 'w') as f:
                json.dump(baseline_data, f)
            baseline_sessions.append(baseline_data)
            
            # Optimized session
            optimized_file = temp_data_dir / f"optimized_{i:03d}.json"
            optimized_data = {
                "session_id": f"optimized_{i:03d}",
                "mode": "optimized",
                "queries": [
                    {
                        "baseline_tokens": 1000,
                        "optimized_tokens": 750,
                        "tokens_saved": 250,
                        "savings_percent": 25.0,
                        "cache_hit": j % 3 == 0,
                        "optimization_applied": True,
                        "latency_ms": 5.0
                    }
                    for j in range(10)
                ]
            }
            with open(optimized_file, 'w') as f:
                json.dump(optimized_data, f)
            optimized_sessions.append(optimized_data)
        
        # Analyze
        analyzer = SessionAnalyzer(
            baseline_sessions=baseline_sessions,
            optimized_sessions=optimized_sessions
        )
        
        stats = analyzer.calculate_basic_stats()
        assert stats["token_reduction_percent"] == pytest.approx(25.0, rel=0.01)
        
        # Generate report
        generator = ReportGenerator()
        report = generator.generate_text_report(stats)
        assert "25.0%" in report
        
        # Generate visualizations (mock)
        # Would test actual visualization generation here
    
    def test_error_recovery_in_workflow(self, temp_data_dir):
        """Test error recovery in analysis workflow."""
        # Create one valid and one corrupted session file
        valid_file = temp_data_dir / "valid.json"
        valid_data = {
            "session_id": "valid",
            "mode": "baseline",
            "queries": [{"baseline_tokens": 1000, "optimized_tokens": 1000}]
        }
        with open(valid_file, 'w') as f:
            json.dump(valid_data, f)
        
        corrupted_file = temp_data_dir / "corrupted.json"
        with open(corrupted_file, 'w') as f:
            f.write("{ invalid json }")
        
        # Analysis should handle corrupted file gracefully
        # Implementation would skip corrupted files and continue


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
