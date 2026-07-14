"""
Tests for the structured logging module.
"""

import json
import logging
import tempfile
from pathlib import Path

from src.monitoring.logger import (
    LoggerFactory,
    LogLevel,
    StructuredLogger,
    configure_logging,
    get_logger,
)


class TestStructuredLogger:
    """Test StructuredLogger class."""

    def test_initialization(self):
        """Test logger initialization."""
        logger = StructuredLogger("test_component")
        assert logger.component == "test_component"
        assert logger.log_level == logging.INFO

    def test_initialization_with_custom_level(self):
        """Test logger initialization with custom log level."""
        logger = StructuredLogger("test", log_level="DEBUG")
        assert logger.log_level == logging.DEBUG

    def test_initialization_with_file(self):
        """Test logger initialization with file output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            logger = StructuredLogger("test", log_file=log_file)

            logger.info("test_event", key="value")

            assert log_file.exists()
            content = log_file.read_text()
            assert "test_event" in content

    def test_format_message(self):
        """Test message formatting."""
        logger = StructuredLogger("test")
        message = logger._format_message("INFO", "test_event", key="value")

        data = json.loads(message)
        assert data["level"] == "INFO"
        assert data["component"] == "test"
        assert data["event"] == "test_event"
        assert data["key"] == "value"
        assert "timestamp" in data

    def test_debug_logging(self, caplog):
        """Test debug level logging."""
        logger = StructuredLogger("test", log_level="DEBUG", enable_console=False)
        logger.logger.addHandler(logging.StreamHandler())

        with caplog.at_level(logging.DEBUG):
            logger.debug("debug_event", detail="test")

        assert len(caplog.records) == 1
        data = json.loads(caplog.records[0].message)
        assert data["level"] == "DEBUG"
        assert data["event"] == "debug_event"

    def test_info_logging(self, caplog):
        """Test info level logging."""
        logger = StructuredLogger("test", enable_console=False)
        logger.logger.addHandler(logging.StreamHandler())

        with caplog.at_level(logging.INFO):
            logger.info("info_event", detail="test")

        assert len(caplog.records) == 1
        data = json.loads(caplog.records[0].message)
        assert data["level"] == "INFO"

    def test_warning_logging(self, caplog):
        """Test warning level logging."""
        logger = StructuredLogger("test", enable_console=False)
        logger.logger.addHandler(logging.StreamHandler())

        with caplog.at_level(logging.WARNING):
            logger.warning("warning_event", detail="test")

        assert len(caplog.records) == 1
        data = json.loads(caplog.records[0].message)
        assert data["level"] == "WARNING"

    def test_error_logging(self, caplog):
        """Test error level logging."""
        logger = StructuredLogger("test", enable_console=False)
        logger.logger.addHandler(logging.StreamHandler())

        with caplog.at_level(logging.ERROR):
            logger.error("error_event", detail="test")

        assert len(caplog.records) == 1
        data = json.loads(caplog.records[0].message)
        assert data["level"] == "ERROR"

    def test_critical_logging(self, caplog):
        """Test critical level logging."""
        logger = StructuredLogger("test", enable_console=False)
        logger.logger.addHandler(logging.StreamHandler())

        with caplog.at_level(logging.CRITICAL):
            logger.critical("critical_event", detail="test")

        assert len(caplog.records) == 1
        data = json.loads(caplog.records[0].message)
        assert data["level"] == "CRITICAL"

    def test_log_cache_hit(self, caplog):
        """Test cache hit logging."""
        logger = StructuredLogger("test", enable_console=False)
        logger.logger.addHandler(logging.StreamHandler())

        with caplog.at_level(logging.INFO):
            logger.log_cache_hit("L1", "test_key", 0.5)

        assert len(caplog.records) == 1
        data = json.loads(caplog.records[0].message)
        assert data["event"] == "cache_hit"
        assert data["cache_level"] == "L1"
        assert "key_hash" in data
        assert data["latency_ms"] == 0.5

    def test_log_cache_miss(self, caplog):
        """Test cache miss logging."""
        logger = StructuredLogger("test", enable_console=False)
        logger.logger.addHandler(logging.StreamHandler())

        with caplog.at_level(logging.INFO):
            logger.log_cache_miss("L2", "test_key")

        assert len(caplog.records) == 1
        data = json.loads(caplog.records[0].message)
        assert data["event"] == "cache_miss"
        assert data["cache_level"] == "L2"

    def test_log_optimization(self, caplog):
        """Test optimization logging."""
        logger = StructuredLogger("test", enable_console=False)
        logger.logger.addHandler(logging.StreamHandler())

        with caplog.at_level(logging.INFO):
            logger.log_optimization(1000, 800, 20.0, 5.5)

        assert len(caplog.records) == 1
        data = json.loads(caplog.records[0].message)
        assert data["event"] == "optimization_complete"
        assert data["original_tokens"] == 1000
        assert data["optimized_tokens"] == 800
        assert data["savings_percent"] == 20.0

    def test_log_truncation(self, caplog):
        """Test truncation logging."""
        logger = StructuredLogger("test", enable_console=False)
        logger.logger.addHandler(logging.StreamHandler())

        with caplog.at_level(logging.INFO):
            logger.log_truncation("priority", 1000, 600, 10.0)

        assert len(caplog.records) == 1
        data = json.loads(caplog.records[0].message)
        assert data["event"] == "truncation_complete"
        assert data["strategy"] == "priority"
        assert data["original_length"] == 1000
        assert data["truncated_length"] == 600

    def test_log_error(self, caplog):
        """Test error logging."""
        logger = StructuredLogger("test", enable_console=False)
        logger.logger.addHandler(logging.StreamHandler())

        with caplog.at_level(logging.ERROR):
            logger.log_error("ValueError", "Invalid input", context="test")

        assert len(caplog.records) == 1
        data = json.loads(caplog.records[0].message)
        assert data["event"] == "error_occurred"
        assert data["error_type"] == "ValueError"
        assert data["error_message"] == "Invalid input"
        assert data["context"] == "test"


class TestLoggerFactory:
    """Test LoggerFactory class."""

    def setup_method(self):
        """Clear loggers before each test."""
        LoggerFactory.clear_loggers()

    def test_get_logger(self):
        """Test getting logger from factory."""
        logger = LoggerFactory.get_logger("test")
        assert isinstance(logger, StructuredLogger)
        assert logger.component == "test"

    def test_get_logger_caching(self):
        """Test that factory caches loggers."""
        logger1 = LoggerFactory.get_logger("test")
        logger2 = LoggerFactory.get_logger("test")
        assert logger1 is logger2

    def test_get_logger_with_custom_level(self):
        """Test getting logger with custom level."""
        logger = LoggerFactory.get_logger("test", log_level="DEBUG")
        assert logger.log_level == logging.DEBUG

    def test_configure(self):
        """Test factory configuration."""
        LoggerFactory.configure(log_level="DEBUG")
        logger = LoggerFactory.get_logger("test")
        assert logger.log_level == logging.DEBUG

    def test_configure_with_log_dir(self):
        """Test factory configuration with log directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir)
            LoggerFactory.configure(log_dir=log_dir)
            logger = LoggerFactory.get_logger("test")

            logger.info("test_event")

            log_file = log_dir / "test.log"
            assert log_file.exists()

    def test_clear_loggers(self):
        """Test clearing cached loggers."""
        logger1 = LoggerFactory.get_logger("test")
        LoggerFactory.clear_loggers()
        logger2 = LoggerFactory.get_logger("test")
        assert logger1 is not logger2


class TestConvenienceFunctions:
    """Test convenience functions."""

    def setup_method(self):
        """Clear loggers before each test."""
        LoggerFactory.clear_loggers()

    def test_get_logger(self):
        """Test get_logger convenience function."""
        logger = get_logger("test")
        assert isinstance(logger, StructuredLogger)
        assert logger.component == "test"

    def test_configure_logging(self):
        """Test configure_logging convenience function."""
        configure_logging(log_level="DEBUG")
        logger = get_logger("test")
        assert logger.log_level == logging.DEBUG

    def test_configure_logging_with_dir(self):
        """Test configure_logging with directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir)
            configure_logging(log_dir=log_dir)
            logger = get_logger("test")

            logger.info("test_event")

            log_file = log_dir / "test.log"
            assert log_file.exists()


class TestLogLevel:
    """Test LogLevel enum."""

    def test_log_levels(self):
        """Test log level values."""
        assert LogLevel.DEBUG.value == "DEBUG"
        assert LogLevel.INFO.value == "INFO"
        assert LogLevel.WARNING.value == "WARNING"
        assert LogLevel.ERROR.value == "ERROR"
        assert LogLevel.CRITICAL.value == "CRITICAL"
