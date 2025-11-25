"""
Middleware for tracking endpoint response times and generating performance metrics.
"""
import time
import logging
from collections import defaultdict
from datetime import datetime
from typing import Dict, List
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


logger = logging.getLogger(__name__)


class ResponseTimeTracker:
    """
    Tracks response times for API endpoints.
    Stores time-series data for analysis and visualization.
    """
    
    def __init__(self):
        # Structure: {endpoint: [(timestamp, response_time_ms, status_code), ...]}
        self.metrics: Dict[str, List[tuple]] = defaultdict(list)
        self.max_records_per_endpoint = 1000  # Prevent memory overflow
    
    def record(self, endpoint: str, response_time_ms: float, status_code: int, timestamp: datetime = None):
        """Record a response time measurement."""
        if timestamp is None:
            timestamp = datetime.now()
        
        self.metrics[endpoint].append((timestamp, response_time_ms, status_code))
        
        # Keep only the latest N records
        if len(self.metrics[endpoint]) > self.max_records_per_endpoint:
            self.metrics[endpoint] = self.metrics[endpoint][-self.max_records_per_endpoint:]
    
    def get_stats(self, endpoint: str = None) -> dict:
        """
        Get statistics for an endpoint or all endpoints.
        
        Returns:
            dict with keys: endpoint, count, avg_ms, min_ms, max_ms, p50_ms, p95_ms, p99_ms
        """
        if endpoint:
            return self._calculate_stats(endpoint, self.metrics.get(endpoint, []))
        
        # Return stats for all endpoints
        all_stats = {}
        for ep, data in self.metrics.items():
            all_stats[ep] = self._calculate_stats(ep, data)
        return all_stats
    
    def _calculate_stats(self, endpoint: str, data: List[tuple]) -> dict:
        """Calculate statistics from recorded data."""
        if not data:
            return {
                "endpoint": endpoint,
                "count": 0,
                "avg_ms": 0,
                "min_ms": 0,
                "max_ms": 0,
                "p50_ms": 0,
                "p95_ms": 0,
                "p99_ms": 0,
                "success_rate": 0,
            }
        
        response_times = [rt for _, rt, _ in data]
        status_codes = [sc for _, _, sc in data]
        
        # Sort for percentile calculations
        sorted_times = sorted(response_times)
        count = len(sorted_times)
        
        # Calculate percentiles
        p50_idx = int(count * 0.50)
        p95_idx = int(count * 0.95)
        p99_idx = int(count * 0.99)
        
        # Calculate success rate (2xx and 3xx status codes)
        successful = sum(1 for sc in status_codes if 200 <= sc < 400)
        
        return {
            "endpoint": endpoint,
            "count": count,
            "avg_ms": round(sum(response_times) / count, 2),
            "min_ms": round(min(response_times), 2),
            "max_ms": round(max(response_times), 2),
            "p50_ms": round(sorted_times[p50_idx], 2),
            "p95_ms": round(sorted_times[p95_idx], 2),
            "p99_ms": round(sorted_times[p99_idx], 2),
            "success_rate": round((successful / count) * 100, 2),
        }
    
    def get_time_series(self, endpoint: str) -> List[dict]:
        """Get time-series data for plotting."""
        data = self.metrics.get(endpoint, [])
        return [
            {
                "timestamp": ts,
                "response_time_ms": rt,
                "status_code": sc
            }
            for ts, rt, sc in data
        ]
    
    def clear(self, endpoint: str = None):
        """Clear metrics for a specific endpoint or all endpoints."""
        if endpoint:
            self.metrics.pop(endpoint, None)
        else:
            self.metrics.clear()


class ResponseTimeMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware to automatically track response times for all endpoints.
    """
    
    def __init__(self, app, tracker: ResponseTimeTracker):
        super().__init__(app)
        self.tracker = tracker
    
    async def dispatch(self, request: Request, call_next):
        # Skip tracking for static files and health checks if desired
        path = request.url.path
        
        # Skip these paths
        skip_paths = ["/docs", "/redoc", "/openapi.json", "/favicon.ico", "/metrics", "/internal"]
        if any(path.startswith(skip) for skip in skip_paths):
            return await call_next(request)
        
        # Start timer
        start_time = time.perf_counter()
        
        # Process request
        response = await call_next(request)
        
        # Calculate response time
        end_time = time.perf_counter()
        response_time_ms = (end_time - start_time) * 1000
        
        # Create endpoint identifier (method + path)
        endpoint = f"{request.method} {path}"
        
        # Record metrics
        self.tracker.record(endpoint, response_time_ms, response.status_code)
        
        # Add response time header
        response.headers["X-Response-Time"] = f"{response_time_ms:.2f}ms"
        
        # Log slow requests (> 1 second)
        if response_time_ms > 1000:
            logger.warning(f"Slow request: {endpoint} took {response_time_ms:.2f}ms")
        
        return response
