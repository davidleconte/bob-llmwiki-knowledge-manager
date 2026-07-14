"""
Structured logging module for the Token Optimization System.

Provides JSON-formatted logging with multiple log levels and automatic
context enrichment for production monitoring and debugging.
"""

import json
import logging
import sys
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional


class LogLevel(Enum):
    """Log level enumeration."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class StructuredLogger:
    """
    Structured logger that outputs JSON-formatted log messages.
    
    Features:
    - JSON-formatted output for easy parsing
    - Automatic timestamp and context enrichment
    - Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - Optional file output with rotation
    - Performance tracking
    
    Example:
        >>> logger = StructuredLogger("cache")
        >>> logger.info("cache_hit", key="abc123", latency_ms=0.5)
        {"timestamp": "2026-07-12T13:30:00.000Z", "level": "INFO", ...}
    """

    def __init__(
        self,
        component: str,
        log_level: str = "INFO",
        log_file: Optional[Path] = None,
        enable_console: bool = True
    ):
        """
        Initialize structured logger.
        
        Args:
            component: Component name (e.g., "cache", "optimizer")
            log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Optional file path for log output
            enable_console: Whether to output to console
        """
        self.component = component
        self.log_level = getattr(logging, log_level.upper())

        # Create logger
        self.logger = logging.getLogger(f"token_optimizer.{component}")
        self.logger.setLevel(self.log_level)
        self.logger.handlers.clear()  # Clear any existing handlers

        # JSON formatter
        formatter = logging.Formatter('%(message)s')

        # Console handler
        if enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.log_level)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

        # File handler
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(self.log_level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def _format_message(
        self,
        level: str,
        event: str,
        **kwargs: Any
    ) -> str:
        """
        Format log message as JSON.
        
        Args:
            level: Log level
            event: Event name
            **kwargs: Additional context fields
            
        Returns:
            JSON-formatted log message
        """
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "level": level,
            "component": self.component,
            "event": event,
            **kwargs
        }
        return json.dumps(log_entry)

    def debug(self, event: str, **kwargs: Any) -> None:
        """Log debug message."""
        self.logger.debug(self._format_message("DEBUG", event, **kwargs))

    def info(self, event: str, **kwargs: Any) -> None:
        """Log info message."""
        self.logger.info(self._format_message("INFO", event, **kwargs))

    def warning(self, event: str, **kwargs: Any) -> None:
        """Log warning message."""
        self.logger.warning(self._format_message("WARNING", event, **kwargs))

    def error(self, event: str, **kwargs: Any) -> None:
        """Log error message."""
        self.logger.error(self._format_message("ERROR", event, **kwargs))

    def critical(self, event: str, **kwargs: Any) -> None:
        """Log critical message."""
        self.logger.critical(self._format_message("CRITICAL", event, **kwargs))

    def log_cache_hit(
        self,
        cache_level: str,
        key: str,
        latency_ms: float
    ) -> None:
        """
        Log cache hit event.
        
        Args:
            cache_level: Cache level (L1, L2)
            key: Cache key (hashed for privacy)
            latency_ms: Lookup latency in milliseconds
        """
        self.info(
            "cache_hit",
            cache_level=cache_level,
            key_hash=hash(key) % 10000,  # Hash for privacy
            latency_ms=round(latency_ms, 2)
        )

    def log_cache_miss(
        self,
        cache_level: str,
        key: str
    ) -> None:
        """
        Log cache miss event.
        
        Args:
            cache_level: Cache level (L1, L2)
            key: Cache key (hashed for privacy)
        """
        self.info(
            "cache_miss",
            cache_level=cache_level,
            key_hash=hash(key) % 10000
        )

    def log_optimization(
        self,
        original_tokens: int,
        optimized_tokens: int,
        savings_percent: float,
        latency_ms: float
    ) -> None:
        """
        Log optimization event.
        
        Args:
            original_tokens: Original token count
            optimized_tokens: Optimized token count
            savings_percent: Percentage of tokens saved
            latency_ms: Optimization latency in milliseconds
        """
        self.info(
            "optimization_complete",
            original_tokens=original_tokens,
            optimized_tokens=optimized_tokens,
            savings_percent=round(savings_percent, 2),
            latency_ms=round(latency_ms, 2)
        )

    def log_truncation(
        self,
        strategy: str,
        original_length: int,
        truncated_length: int,
        latency_ms: float
    ) -> None:
        """
        Log truncation event.
        
        Args:
            strategy: Truncation strategy used
            original_length: Original text length
            truncated_length: Truncated text length
            latency_ms: Truncation latency in milliseconds
        """
        self.info(
            "truncation_complete",
            strategy=strategy,
            original_length=original_length,
            truncated_length=truncated_length,
            reduction_percent=round((1 - truncated_length/original_length) * 100, 2),
            latency_ms=round(latency_ms, 2)
        )

    def log_error(
        self,
        error_type: str,
        error_message: str,
        **kwargs: Any
    ) -> None:
        """
        Log error event.
        
        Args:
            error_type: Type of error
            error_message: Error message
            **kwargs: Additional context
        """
        self.error(
            "error_occurred",
            error_type=error_type,
            error_message=error_message,
            **kwargs
        )


class LoggerFactory:
    """
    Factory for creating component-specific loggers.
    
    Ensures consistent logging configuration across all components.
    """

    _loggers: Dict[str, StructuredLogger] = {}
    _default_log_level = "INFO"
    _default_log_dir: Optional[Path] = None

    @classmethod
    def configure(
        cls,
        log_level: str = "INFO",
        log_dir: Optional[Path] = None
    ) -> None:
        """
        Configure global logging settings.
        
        Args:
            log_level: Default log level
            log_dir: Directory for log files
        """
        cls._default_log_level = log_level
        cls._default_log_dir = log_dir

    @classmethod
    def get_logger(
        cls,
        component: str,
        log_level: Optional[str] = None
    ) -> StructuredLogger:
        """
        Get or create logger for component.
        
        Args:
            component: Component name
            log_level: Optional override for log level
            
        Returns:
            StructuredLogger instance
        """
        if component not in cls._loggers:
            level = log_level or cls._default_log_level
            log_file = None
            if cls._default_log_dir:
                log_file = cls._default_log_dir / f"{component}.log"

            cls._loggers[component] = StructuredLogger(
                component=component,
                log_level=level,
                log_file=log_file
            )

        return cls._loggers[component]

    @classmethod
    def clear_loggers(cls) -> None:
        """Clear all cached loggers."""
        cls._loggers.clear()


# Convenience functions for quick logging
def get_logger(component: str) -> StructuredLogger:
    """
    Get logger for component.
    
    Args:
        component: Component name
        
    Returns:
        StructuredLogger instance
    """
    return LoggerFactory.get_logger(component)


def configure_logging(log_level: str = "INFO", log_dir: Optional[Path] = None) -> None:
    """
    Configure global logging settings.
    
    Args:
        log_level: Default log level
        log_dir: Directory for log files
    """
    LoggerFactory.configure(log_level, log_dir)
