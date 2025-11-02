import argparse
import logging
import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

parser = argparse.ArgumentParser(description='SocioLens Web Server')
parser.add_argument('-n', '--num-gpus', type=int, default=1, help='Number of GPUs to use (default: 1)')
parser.add_argument('-p', '--port', type=int, default=8000, help='Port to run the server on')
parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind the server to')
parser.add_argument('--debug', action='store_true')
args = parser.parse_args()

templates = Jinja2Templates(directory="content")

SERVICES = {
    "SocioLens API": "http://localhost:8000/",
    "GitHub": "https://api.github.com",
    "Google": "https://www.google.com",
    "FastAPI": "https://fastapi.tiangolo.com"
}

# Health state
health_data = {name: {"url": url, "status": "Unknown", "last_checked": None} for name, url in SERVICES.items()}


logging.basicConfig(
    level=logging.DEBUG if args.debug else logging.INFO,
    format='%(asctime)s [%(levelname)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


app = FastAPI()

@app.get("/health")
def health(request: Request, response_class=HTMLResponse):
    return templates.TemplateResponse("health.html", {"request": request, "services": health_data})
    
    
@app.get("/pid")
def pid():
    return {
        "pid": os.getpid()
    }


@app.get("/")
def root(request: Request):
    return {"status": "ok", "msg": "SocioLens ASGI server" }

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting web server on {args.host}:{args.port}")

    if args.debug:
        # Works only if the module name can be imported (e.g., app.py)
        module_name = os.path.splitext(os.path.basename(__file__))[0]
        uvicorn.run(f"{module_name}:app", host=args.host, port=args.port, reload=True)
    else:
        uvicorn.run(app, host=args.host, port=args.port, reload=False)
