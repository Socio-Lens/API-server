# app/routes/health.py\
import os
import logging
from utils.functions import humanize_time
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

logger = logging.getLogger(__name__)

SERVICES = {
    "SocioLens API": {
        "route": "service",
        "last_checked": None,
        "status": "Not ready"
    }
}

def _should_update(last_checked: datetime | None, threshold_minutes: int = 10) -> bool:
    """Return True if last_checked is None or older than threshold_minutes."""
    if last_checked is None:
        return True
    now = datetime.now(timezone.utc)
    return (now - last_checked) > timedelta(minutes=threshold_minutes)

templates = Jinja2Templates(directory="templates")
health_data = {name: {"url": url, "status": "Unknown", "last_checked": None} for name, url in SERVICES.items()}
router = APIRouter(prefix="/internal", tags=["internal"])


@router.get("/pid")
def pid():
    return {"pid": os.getpid()}

@router.get("/health", response_class=HTMLResponse)
def health(request: Request):


        
    for name, meta in SERVICES.items():
        if _should_update(meta['last_checked']):
            logger.debug(name)
            if name == 'SocioLens API':
                worker_pool = request.app.state.worker_pool
                ready = worker_pool is not None and getattr(worker_pool, "workers", None) and len(worker_pool.workers) > 0
                SERVICES[name]["status"] = "Ready" if ready else "Not ready"
                
            SERVICES[name]['last_checked'] = datetime.now(timezone.utc)
            
    health_data = { name: { 'route': meta['route'], 'status': meta['status'], 'last_checked': humanize_time(meta['last_checked']) } for name, meta in SERVICES.items() }
            
    return templates.TemplateResponse("health.html", { "request": request, 'services': health_data })

@router.get("/workers")
def health(request: Request):
    
    worker_pool = getattr(request.app.state, 'worker_pool', None)
    return {
        "status": "ok",
        "ready": worker_pool is not None and len(worker_pool.workers) > 0,
        "num_gpus": worker_pool.num_gpus if worker_pool else 0,
        "available_workers": worker_pool.available_workers.qsize() if worker_pool else 0
    }
    


