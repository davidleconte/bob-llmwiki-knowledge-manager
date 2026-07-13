"""
Health check module for the Token Optimization System.

Provides system health monitoring and status checks for all components.
"""

import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import sys

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class HealthStatus(Enum):
    """Health status enumeration."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class ComponentHealth:
    """Health status for a component."""
    name: str
    status: HealthStatus
    message: str
    latency_ms: Optional[float] = None
    details: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "name": self.name,
            "status": self.status.value,
            "message": self.message
        }
        if self.latency_ms is not None:
            result["latency_ms"] = round(self.latency_ms, 2)
        if self.details:
            result["details"] = self.details
        return result


class HealthChecker:
    """
    System health checker.
    
    Monitors health of all system components and provides
    overall system health status.
    
    Example:
        >>> checker = HealthChecker()
        >>> health = checker.check_health()
        >>> print(health["status"])
        "healthy"
    """
    
    def __init__(
        self,
        cache_l1=None,
        cache_l2=None,
        optimizer=None,
        truncator=None
    ):
        """
        Initialize health checker.
        
        Args:
            cache_l1: L1 cache instance
            cache_l2: L2 cache instance
            optimizer: Optimizer instance
            truncator: Truncator instance
        """
        self.cache_l1 = cache_l1
        self.cache_l2 = cache_l2
        self.optimizer = optimizer
        self.truncator = truncator
        self._start_time = time.time()
    
    def check_cache_health(self, cache, name: str) -> ComponentHealth:
        """
        Check cache health.
        
        Args:
            cache: Cache instance
            name: Cache name
            
        Returns:
            ComponentHealth instance
        """
        if cache is None:
            return ComponentHealth(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message="Cache not initialized"
            )
        
        try:
            start = time.time()
            
            # Try a test operation
            test_key = "__health_check__"
            cache.get(test_key)
            
            latency_ms = (time.time() - start) * 1000
            
            # Get cache stats
            stats = cache.stats()
            
            # Determine health based on hit rate and latency
            hit_rate = stats.get("hit_rate", 0)
            
            if latency_ms > 100:
                status = HealthStatus.DEGRADED
                message = f"High latency: {latency_ms:.2f}ms"
            elif hit_rate < 5 and stats.get("total_requests", 0) > 100:
                status = HealthStatus.DEGRADED
                message = f"Low hit rate: {hit_rate:.2f}%"
            else:
                status = HealthStatus.HEALTHY
                message = "Operating normally"
            
            return ComponentHealth(
                name=name,
                status=status,
                message=message,
                latency_ms=latency_ms,
                details={
                    "hit_rate": round(hit_rate, 2),
                    "total_requests": stats.get("total_requests", 0),
                    "size": stats.get("size", 0)
                }
            )
            
        except Exception as e:
            return ComponentHealth(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=f"Error: {str(e)}"
            )
    
    def check_optimizer_health(self) -> ComponentHealth:
        """
        Check optimizer health.
        
        Returns:
            ComponentHealth instance
        """
        if self.optimizer is None:
            return ComponentHealth(
                name="optimizer",
                status=HealthStatus.UNHEALTHY,
                message="Optimizer not initialized"
            )
        
        try:
            start = time.time()
            
            # Try a test optimization
            test_text = "This is a test prompt for health checking."
            result = self.optimizer.optimize(test_text)
            
            latency_ms = (time.time() - start) * 1000
            
            # Check if optimization worked
            if result.get("optimized") and latency_ms < 100:
                status = HealthStatus.HEALTHY
                message = "Operating normally"
            elif latency_ms >= 100:
                status = HealthStatus.DEGRADED
                message = f"High latency: {latency_ms:.2f}ms"
            else:
                status = HealthStatus.DEGRADED
                message = "Optimization may not be working correctly"
            
            return ComponentHealth(
                name="optimizer",
                status=status,
                message=message,
                latency_ms=latency_ms
            )
            
        except Exception as e:
            return ComponentHealth(
                name="optimizer",
                status=HealthStatus.UNHEALTHY,
                message=f"Error: {str(e)}"
            )
    
    def check_truncator_health(self) -> ComponentHealth:
        """
        Check truncator health.
        
        Returns:
            ComponentHealth instance
        """
        if self.truncator is None:
            return ComponentHealth(
                name="truncator",
                status=HealthStatus.UNHEALTHY,
                message="Truncator not initialized"
            )
        
        try:
            start = time.time()
            
            # Try a test truncation
            test_text = "This is a test text for health checking. " * 100
            result = self.truncator.truncate(test_text, max_tokens=100)
            
            latency_ms = (time.time() - start) * 1000
            
            # Check if truncation worked
            if len(result) <= 100 and latency_ms < 50:
                status = HealthStatus.HEALTHY
                message = "Operating normally"
            elif latency_ms >= 50:
                status = HealthStatus.DEGRADED
                message = f"High latency: {latency_ms:.2f}ms"
            else:
                status = HealthStatus.DEGRADED
                message = "Truncation may not be working correctly"
            
            return ComponentHealth(
                name="truncator",
                status=status,
                message=message,
                latency_ms=latency_ms
            )
            
        except Exception as e:
            return ComponentHealth(
                name="truncator",
                status=HealthStatus.UNHEALTHY,
                message=f"Error: {str(e)}"
            )
    
    def check_system_resources(self) -> ComponentHealth:
        """
        Check system resource usage.
        
        Returns:
            ComponentHealth instance
        """
        if not PSUTIL_AVAILABLE:
            return ComponentHealth(
                name="system_resources",
                status=HealthStatus.DEGRADED,
                message="psutil not available - install with: pip install psutil"
            )
        
        try:
            # Get CPU and memory usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Determine health based on resource usage
            if cpu_percent > 90 or memory_percent > 90:
                status = HealthStatus.UNHEALTHY
                message = "Critical resource usage"
            elif cpu_percent > 70 or memory_percent > 70:
                status = HealthStatus.DEGRADED
                message = "High resource usage"
            else:
                status = HealthStatus.HEALTHY
                message = "Normal resource usage"
            
            return ComponentHealth(
                name="system_resources",
                status=status,
                message=message,
                details={
                    "cpu_percent": round(cpu_percent, 2),
                    "memory_percent": round(memory_percent, 2),
                    "memory_available_mb": round(memory.available / 1024 / 1024, 2)
                }
            )
            
        except Exception as e:
            return ComponentHealth(
                name="system_resources",
                status=HealthStatus.DEGRADED,
                message=f"Could not check resources: {str(e)}"
            )
    
    def check_health(self) -> Dict[str, Any]:
        """
        Check overall system health.
        
        Returns:
            Dictionary containing health status for all components
        """
        components: List[ComponentHealth] = []
        
        # Check cache health
        if self.cache_l1:
            components.append(self.check_cache_health(self.cache_l1, "cache_l1"))
        if self.cache_l2:
            components.append(self.check_cache_health(self.cache_l2, "cache_l2"))
        
        # Check optimizer health
        if self.optimizer:
            components.append(self.check_optimizer_health())
        
        # Check truncator health
        if self.truncator:
            components.append(self.check_truncator_health())
        
        # Check system resources
        components.append(self.check_system_resources())
        
        # Determine overall status
        unhealthy_count = sum(1 for c in components if c.status == HealthStatus.UNHEALTHY)
        degraded_count = sum(1 for c in components if c.status == HealthStatus.DEGRADED)
        
        if unhealthy_count > 0:
            overall_status = HealthStatus.UNHEALTHY
            overall_message = f"{unhealthy_count} component(s) unhealthy"
        elif degraded_count > 0:
            overall_status = HealthStatus.DEGRADED
            overall_message = f"{degraded_count} component(s) degraded"
        else:
            overall_status = HealthStatus.HEALTHY
            overall_message = "All components healthy"
        
        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "status": overall_status.value,
            "message": overall_message,
            "uptime_seconds": round(time.time() - self._start_time, 2),
            "components": [c.to_dict() for c in components],
            "python_version": sys.version,
            "platform": sys.platform
        }
    
    def is_healthy(self) -> bool:
        """
        Check if system is healthy.
        
        Returns:
            True if system is healthy, False otherwise
        """
        health = self.check_health()
        return health["status"] == HealthStatus.HEALTHY.value


# Global health checker instance
_global_checker: Optional[HealthChecker] = None


def configure_health_checker(
    cache_l1=None,
    cache_l2=None,
    optimizer=None,
    truncator=None
) -> None:
    """
    Configure global health checker.
    
    Args:
        cache_l1: L1 cache instance
        cache_l2: L2 cache instance
        optimizer: Optimizer instance
        truncator: Truncator instance
    """
    global _global_checker
    _global_checker = HealthChecker(
        cache_l1=cache_l1,
        cache_l2=cache_l2,
        optimizer=optimizer,
        truncator=truncator
    )


def get_health_checker() -> HealthChecker:
    """
    Get global health checker instance.
    
    Returns:
        HealthChecker instance
    """
    global _global_checker
    if _global_checker is None:
        _global_checker = HealthChecker()
    return _global_checker


def check_health() -> Dict[str, Any]:
    """
    Check system health using global checker.
    
    Returns:
        Health status dictionary
    """
    return get_health_checker().check_health()
