"""
Metrics and monitoring endpoints.
"""
import logging
from datetime import datetime
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/metrics", tags=["metrics"])
templates = Jinja2Templates(directory="templates")


@router.get(
    "/stats",
    name="metrics_stats",
    summary="Get performance statistics for all endpoints"
)
async def get_stats(request: Request, endpoint: str = None):
    """
    Get response time statistics.
    
    Query params:
        endpoint: Optional specific endpoint to get stats for (e.g., "POST /service/sentiment/base")
    """
    tracker = request.app.state.response_tracker
    
    if endpoint:
        stats = tracker.get_stats(endpoint)
        if not stats or stats.get("count", 0) == 0:
            raise HTTPException(status_code=404, detail=f"No data found for endpoint: {endpoint}")
        return stats
    
    stats = tracker.get_stats()
    return {
        "total_endpoints": len(stats),
        "endpoints": stats
    }


@router.get(
    "/timeseries",
    name="metrics_timeseries",
    summary="Get time-series data for an endpoint"
)
async def get_timeseries(request: Request, endpoint: str):
    """
    Get raw time-series data for plotting.
    
    Query params:
        endpoint: Endpoint identifier (e.g., "POST /service/sentiment/base")
    """
    tracker = request.app.state.response_tracker
    data = tracker.get_time_series(endpoint)
    
    if not data:
        raise HTTPException(status_code=404, detail=f"No data found for endpoint: {endpoint}")
    
    return {
        "endpoint": endpoint,
        "count": len(data),
        "data": data
    }


@router.get(
    "/dashboard",
    name="metrics_dashboard",
    summary="View performance metrics dashboard",
    response_class=HTMLResponse
)
async def get_dashboard(request: Request):
    """
    View an HTML dashboard with performance metrics for all endpoints.
    """
    tracker = request.app.state.response_tracker
    stats = tracker.get_stats()
    
    # Calculate overall metrics
    total_requests = sum(s['count'] for s in stats.values())
    total_endpoints = len(stats)
    
    if total_requests > 0:
        overall_avg_ms = sum(s['avg_ms'] * s['count'] for s in stats.values()) / total_requests
        overall_success_rate = sum(s['success_rate'] * s['count'] for s in stats.values()) / total_requests
    else:
        overall_avg_ms = 0
        overall_success_rate = 100
    
    return templates.TemplateResponse(
        "metrics.html",
        {
            "request": request,
            "endpoints": stats,
            "total_endpoints": total_endpoints,
            "total_requests": total_requests,
            "overall_avg_ms": overall_avg_ms,
            "overall_success_rate": overall_success_rate,
            "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    )



@router.post(
    "/clear",
    name="metrics_clear",
    summary="Clear metrics data"
)
async def clear_metrics(request: Request, endpoint: str = None):
    """
    Clear metrics for a specific endpoint or all endpoints.
    
    Query params:
        endpoint: Optional specific endpoint to clear
    """
    tracker = request.app.state.response_tracker
    tracker.clear(endpoint)
    
    return {
        "status": "success",
        "message": f"Cleared metrics for {endpoint if endpoint else 'all endpoints'}"
    }
