# logger

Structured logging module for the Token Optimization System.

Provides JSON-formatted logging with multiple log levels and automatic
context enrichment for production monitoring and debugging.

## Constants

- `DEBUG`
- `INFO`
- `WARNING`
- `ERROR`
- `CRITICAL`

## Functions

### `get_logger(component: str) -> StructuredLogger`

Get logger for component.

Args:
    component: Component name

Returns:
    StructuredLogger instance


### `configure_logging(log_level: str, log_dir: Optional[Path]) -> None`

Configure global logging settings.

Args:
    log_level: Default log level
    log_dir: Directory for log files


## Classes

### `LogLevel(Enum)`

Log level enumeration.


### `StructuredLogger`

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

#### Methods

##### `__init__(component: str, log_level: str, log_file: Optional[Path], enable_console: bool)`

Initialize structured logger.

Args:
    component: Component name (e.g., "cache", "optimizer")
    log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    log_file: Optional file path for log output
    enable_console: Whether to output to console


##### `debug(event: str) -> None`

Log debug message.


##### `info(event: str) -> None`

Log info message.


##### `warning(event: str) -> None`

Log warning message.


##### `error(event: str) -> None`

Log error message.


##### `critical(event: str) -> None`

Log critical message.


##### `log_cache_hit(cache_level: str, key: str, latency_ms: float) -> None`

Log cache hit event.

Args:
    cache_level: Cache level (L1, L2)
    key: Cache key (hashed for privacy)
    latency_ms: Lookup latency in milliseconds


##### `log_cache_miss(cache_level: str, key: str) -> None`

Log cache miss event.

Args:
    cache_level: Cache level (L1, L2)
    key: Cache key (hashed for privacy)


##### `log_optimization(original_tokens: int, optimized_tokens: int, savings_percent: float, latency_ms: float) -> None`

Log optimization event.

Args:
    original_tokens: Original token count
    optimized_tokens: Optimized token count
    savings_percent: Percentage of tokens saved
    latency_ms: Optimization latency in milliseconds


##### `log_truncation(strategy: str, original_length: int, truncated_length: int, latency_ms: float) -> None`

Log truncation event.

Args:
    strategy: Truncation strategy used
    original_length: Original text length
    truncated_length: Truncated text length
    latency_ms: Truncation latency in milliseconds


##### `log_error(error_type: str, error_message: str) -> None`

Log error event.

Args:
    error_type: Type of error
    error_message: Error message
    **kwargs: Additional context



### `LoggerFactory`

Factory for creating component-specific loggers.

Ensures consistent logging configuration across all components.

#### Methods

##### `configure(cls, log_level: str, log_dir: Optional[Path]) -> None`

Configure global logging settings.

Args:
    log_level: Default log level
    log_dir: Directory for log files


##### `get_logger(cls, component: str, log_level: Optional[str]) -> StructuredLogger`

Get or create logger for component.

Args:
    component: Component name
    log_level: Optional override for log level

Returns:
    StructuredLogger instance


##### `clear_loggers(cls) -> None`

Clear all cached loggers.


