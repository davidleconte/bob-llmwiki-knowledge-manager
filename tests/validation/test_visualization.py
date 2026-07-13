"""
Tests for Visualization Tools

Tests the chart generation and visualization functionality
used for Phase 3 validation reporting.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Mock matplotlib before importing visualization module
sys.modules['matplotlib'] = MagicMock()
sys.modules['matplotlib.pyplot'] = MagicMock()
sys.modules['matplotlib.figure'] = MagicMock()
sys.modules['matplotlib.axes'] = MagicMock()

from examples.visualization import (
    SessionVisualizer
)


class TestSessionVisualizer:
    """Test SessionVisualizer class."""
    
    @pytest.fixture
    def mock_stats(self):
        """Provide mock statistics for visualization."""
        return {
            "baseline_sessions": [
                {"session_id": f"baseline_{i:03d}", "total_tokens": 10000}
                for i in range(10)
            ],
            "optimized_sessions": [
                {"session_id": f"optimized_{i:03d}", "total_tokens": 7500}
                for i in range(10)
            ],
            "cache_hit_rate": 33.33,
            "optimization_rate": 100.0,
            "truncation_rate": 50.0,
            "latency_data": [5.0, 5.5, 4.8, 5.2, 5.1] * 20,
            "savings_over_time": [
                {"session": i, "cumulative_savings": i * 2500}
                for i in range(1, 21)
            ]
        }
    
    @pytest.fixture
    def temp_output_dir(self, tmp_path):
        """Provide temporary directory for chart output."""
        output_dir = tmp_path / "charts"
        output_dir.mkdir()
        return output_dir
    
    def test_chart_generator_initialization(self, temp_output_dir):
        """Test SessionVisualizer initialization."""
        generator = SessionVisualizer(output_dir=temp_output_dir)
        
        assert generator.output_dir == temp_output_dir
        assert temp_output_dir.exists()
    
    def test_savings_comparison_chart_creation(self, mock_stats, temp_output_dir):
        """Test savings comparison chart generation."""
        generator = SessionVisualizer(output_dir=temp_output_dir)
        
        chart_file = generator.create_savings_comparison_chart(mock_stats)
        
        assert chart_file is not None
        assert isinstance(chart_file, Path)
        assert chart_file.name == "savings_comparison.png"
    
    def test_cache_effectiveness_chart_creation(self, mock_stats, temp_output_dir):
        """Test cache effectiveness chart generation."""
        generator = SessionVisualizer(output_dir=temp_output_dir)
        
        chart_file = generator.create_cache_effectiveness_chart(mock_stats)
        
        assert chart_file is not None
        assert isinstance(chart_file, Path)
        assert chart_file.name == "cache_effectiveness.png"
    
    def test_latency_distribution_chart_creation(self, mock_stats, temp_output_dir):
        """Test latency distribution chart generation."""
        generator = SessionVisualizer(output_dir=temp_output_dir)
        
        chart_file = generator.create_latency_distribution_chart(mock_stats)
        
        assert chart_file is not None
        assert isinstance(chart_file, Path)
        assert chart_file.name == "latency_distribution.png"
    
    def test_savings_over_time_chart_creation(self, mock_stats, temp_output_dir):
        """Test savings over time chart generation."""
        generator = SessionVisualizer(output_dir=temp_output_dir)
        
        chart_file = generator.create_savings_over_time_chart(mock_stats)
        
        assert chart_file is not None
        assert isinstance(chart_file, Path)
        assert chart_file.name == "savings_over_time.png"
    
    def test_dashboard_creation(self, mock_stats, temp_output_dir):
        """Test dashboard generation."""
        generator = SessionVisualizer(output_dir=temp_output_dir)
        
        dashboard_file = generator.create_dashboard(mock_stats)
        
        assert dashboard_file is not None
        assert isinstance(dashboard_file, Path)
        assert dashboard_file.name == "dashboard.png"
    
    def test_chart_dimensions(self, mock_stats, temp_output_dir):
        """Test that charts have correct dimensions."""
        generator = SessionVisualizer(output_dir=temp_output_dir, figsize=(12, 8))
        
        # Verify figsize is stored
        assert generator.figsize == (12, 8)
    
    def test_chart_dpi_setting(self, mock_stats, temp_output_dir):
        """Test that charts use correct DPI."""
        generator = SessionVisualizer(output_dir=temp_output_dir, dpi=150)
        
        # Verify DPI is stored
        assert generator.dpi == 150
    
    def test_missing_data_handling(self, temp_output_dir):
        """Test handling of missing data in charts."""
        generator = SessionVisualizer(output_dir=temp_output_dir)
        
        incomplete_stats = {
            "baseline_sessions": [],
            "optimized_sessions": []
        }
        
        # Should handle gracefully, not crash
        chart_file = generator.create_savings_comparison_chart(incomplete_stats)
        
        # May return None or create empty chart
        assert chart_file is None or isinstance(chart_file, Path)
    
    def test_invalid_data_handling(self, temp_output_dir):
        """Test handling of invalid data."""
        generator = SessionVisualizer(output_dir=temp_output_dir)
        
        invalid_stats = {
            "baseline_sessions": "not a list",
            "optimized_sessions": None
        }
        
        # Should handle gracefully
        with pytest.raises((TypeError, ValueError, AttributeError)):
            generator.create_savings_comparison_chart(invalid_stats)
    
    def test_output_directory_creation(self, tmp_path):
        """Test that output directory is created if it doesn't exist."""
        non_existent_dir = tmp_path / "new_charts"
        
        generator = SessionVisualizer(output_dir=non_existent_dir)
        
        assert non_existent_dir.exists()
    
    def test_chart_file_overwrite(self, mock_stats, temp_output_dir):
        """Test that existing chart files are overwritten."""
        generator = SessionVisualizer(output_dir=temp_output_dir)
        
        # Create chart twice
        chart_file1 = generator.create_savings_comparison_chart(mock_stats)
        chart_file2 = generator.create_savings_comparison_chart(mock_stats)
        
        # Should be same file
        assert chart_file1 == chart_file2


# Dashboard tests simplified - using SessionVisualizer for all charts


# Additional visualization tests - TODO: Implement when helper functions are added


class TestIntegration:
    """Integration tests for complete visualization workflows."""
    
    @pytest.fixture
    def temp_output_dir(self, tmp_path):
        """Provide temporary directory for integration tests."""
        output_dir = tmp_path / "integration"
        output_dir.mkdir()
        return output_dir
    
    @pytest.fixture
    def complete_stats(self):
        """Provide complete statistics for integration testing."""
        return {
            "total_baseline_queries": 100,
            "total_optimized_queries": 100,
            "total_baseline_tokens": 100000,
            "total_optimized_tokens": 75000,
            "token_reduction_percent": 25.0,
            "cache_hit_rate": 33.33,
            "optimization_rate": 100.0,
            "truncation_rate": 50.0,
            "avg_latency_ms": 5.0,
            "baseline_sessions": [
                {"session_id": f"baseline_{i:03d}", "total_tokens": 10000}
                for i in range(10)
            ],
            "optimized_sessions": [
                {"session_id": f"optimized_{i:03d}", "total_tokens": 7500}
                for i in range(10)
            ],
            "latency_data": [5.0, 5.5, 4.8, 5.2, 5.1] * 20,
            "savings_over_time": [
                {"session": i, "cumulative_savings": i * 2500}
                for i in range(1, 21)
            ]
        }
    
    def test_complete_visualization_workflow(self, complete_stats, temp_output_dir):
        """Test complete visualization workflow."""
        generator = SessionVisualizer(output_dir=temp_output_dir)
        
        # Generate all charts
        charts = {
            "savings": generator.create_savings_comparison_chart(complete_stats),
            "cache": generator.create_cache_effectiveness_chart(complete_stats),
            "latency": generator.create_latency_distribution_chart(complete_stats),
            "time": generator.create_savings_over_time_chart(complete_stats),
            "dashboard": generator.create_dashboard(complete_stats)
        }
        
        # Verify all charts created
        for chart_name, chart_file in charts.items():
            assert chart_file is not None, f"{chart_name} chart not created"
            assert isinstance(chart_file, Path), f"{chart_name} not a Path"
    
    def test_batch_chart_generation(self, complete_stats, temp_output_dir):
        """Test batch generation of all charts."""
        generator = SessionVisualizer(output_dir=temp_output_dir)
        
        chart_files = generator.generate_all_charts(complete_stats)
        
        assert isinstance(chart_files, dict)
        assert len(chart_files) >= 4  # At least 4 chart types
        assert all(isinstance(f, Path) for f in chart_files.values())


class TestErrorHandling:
    """Test error handling in visualization."""
    
    @pytest.fixture
    def temp_output_dir(self, tmp_path):
        """Provide temporary directory."""
        output_dir = tmp_path / "errors"
        output_dir.mkdir()
        return output_dir
    
    def test_matplotlib_import_error_handling(self, temp_output_dir):
        """Test handling when matplotlib is not available."""
        # This is already mocked, but test the fallback behavior
        generator = SessionVisualizer(output_dir=temp_output_dir)
        
        # Should initialize without error even if matplotlib is mocked
        assert generator is not None
    
    def test_invalid_output_directory(self):
        """Test handling of invalid output directory."""
        with pytest.raises((OSError, PermissionError)):
            # Try to create in a location without permissions
            SessionVisualizer(output_dir=Path("/root/forbidden"))
    
    def test_disk_full_handling(self, temp_output_dir, complete_stats):
        """Test handling when disk is full."""
        generator = SessionVisualizer(output_dir=temp_output_dir)
        
        # Mock disk full error
        with patch('matplotlib.pyplot.savefig', side_effect=OSError("No space left")):
            with pytest.raises(OSError):
                generator.create_savings_comparison_chart(complete_stats)


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
