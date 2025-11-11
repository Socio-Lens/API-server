# app/routes/health.py\
import os
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

SERVICES = {
    "SocioLens API": "http://localhost:8000/",
    "GitHub": "https://api.github.com",
    "Google": "https://www.google.com",
    "FastAPI": "https://fastapi.tiangolo.com"
}
templates = Jinja2Templates(directory="templates")
health_data = {name: {"url": url, "status": "Unknown", "last_checked": None} for name, url in SERVICES.items()}
router = APIRouter(prefix="/internal", tags=["internal"])


@router.get("/pid")
def pid():
    return {"pid": os.getpid()}

@router.get("/health", response_class=HTMLResponse)
def health(request: Request):
    return templates.TemplateResponse("health.html", { "request": request, 'services': health_data })
