# app/routes/health.py
import os
import logging
import asyncio
from utils.functions import humanize_time
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Request
from fastapi.routing import APIRoute
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from collections import deque
from utils.healthChecker import healthChecker

logger = logging.getLogger(__name__)

# Store status history (max 90 entries = ~15 hours at 10-min intervals)


def _should_update(last_checked: datetime | None, threshold_minutes: int = 10) -> bool:
    """Return True if last_checked is None or older than threshold_minutes."""
    if last_checked is None:
        return True
    now = datetime.now(timezone.utc)
    return (now - last_checked) > timedelta(minutes=threshold_minutes)

def check_service_status(app):
    """Check the status of services and update history."""
    for name, meta in healthChecker.SERVICES.items():
        if name == 'SocioLens API':
            worker_pool = getattr(app.state, 'worker_pool', None)
            ready = worker_pool is not None and getattr(worker_pool, "workers", None) and len(worker_pool.workers) > 0
            healthChecker.SERVICES[name]["status"] = "Ready" if ready else "Not ready"

        # hacky fix for now :p
        else:
            healthChecker.SERVICES[name]["status"] = "Ready"
            
        healthChecker.SERVICES[name]['last_checked'] = datetime.now(timezone.utc)
        
        # Add to history
        healthChecker.STATUS_HISTORY[name].append({
            "status": healthChecker.SERVICES[name]["status"],
            "timestamp": healthChecker.SERVICES[name]['last_checked']
        })
        
        logger.info(f"Health check: {name} - {healthChecker.SERVICES[name]['status']}")

async def background_health_checker(app):
    """Background task that runs health checks every 10 minutes."""
    logger.info("Starting background health checker")
    
    # Do an initial check immediately
    check_service_status(app)
    
    while True:
        try:
            await asyncio.sleep(600)  # 10 minutes
            check_service_status(app)
        except asyncio.CancelledError:
            logger.info("Background health checker stopped")
            break
        except Exception as e:
            logger.error(f"Error in background health checker: {e}")

templates = Jinja2Templates(directory="templates")
router = APIRouter(prefix="/internal", tags=["internal"])


@router.get("/endpoints")
def get_endpoints(request: Request):
    app = request.app
    routes = []
    for route in app.routes:
        if isinstance(route, APIRoute):
            routes.append({
                "path": route.path,
                "methods": list(route.methods),
                "name": route.name
            })
    return routes

@router.get("/pid")
def pid():
    return {"pid": os.getpid()}

@router.get("/health", response_class=HTMLResponse)
def health(request: Request):
    # Just return the current data, no need to update here
    health_data = { 
        name: { 
            'route': meta['route'], 
            'status': meta['status'], 
            'last_checked': '...' if not meta['last_checked'] else humanize_time(meta['last_checked']),
            'history': list(healthChecker.STATUS_HISTORY[name])
        } 
        for name, meta in healthChecker.SERVICES.items() 
    }
            
    return templates.TemplateResponse("health.html", { "request": request, 'services': health_data })

@router.get("/workers")
def workers(request: Request):
    worker_pool = getattr(request.app.state, 'worker_pool', None)
    return {
        "status": "ok",
        "ready": worker_pool is not None and len(worker_pool.workers) > 0,
        "num_gpus": worker_pool.num_gpus if worker_pool else 0,
        "available_workers": worker_pool.available_workers.qsize() if worker_pool else 0
    }

# Startup event handler - add this to your main FastAPI app
async def start_health_checker(app):
    """Call this from your FastAPI app's startup event."""
    task = asyncio.create_task(background_health_checker(app))
    app.state.health_checker_task = task
    return task

# Shutdown event handler - add this to your FastAPI app's shutdown event
async def stop_health_checker(app):
    """Call this from your FastAPI app's shutdown event."""
    if hasattr(app.state, 'health_checker_task'):
        app.state.health_checker_task.cancel()
        try:
            await app.state.health_checker_task
        except asyncio.CancelledError:
            pass