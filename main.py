import argparse
import logging
import os
import asyncio
from routes.internal import background_health_checker
from utils.router import include_route_modules
from utils.worker import Worker, WorkerPool
from utils.config import Config
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager

parser = argparse.ArgumentParser(description='SocioLens Web Server')
parser.add_argument('-n', '--num-gpus', type=int, default=1, help='Number of GPUs to use (default: 1)')
parser.add_argument('-p', '--port', type=int, default=8000, help='Port to run the server on')
parser.add_argument('--host', type=str, default='127.0.0.1', help='Host to bind the server to')
parser.add_argument('--debug', action='store_true')
args = parser.parse_args()

config = Config()

# --- Logging: guard against double configuration ---
root_logger = logging.getLogger()
if not root_logger.handlers:
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s [%(levelname)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler()],
    )
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Loading models across available GPUs...")
    app.state.worker_pool = WorkerPool()

    await app.state.worker_pool.initialize(config)
    include_route_modules(app)
    
    # Start background health checker as a task (don't await it!)
    health_checker_task = asyncio.create_task(background_health_checker(app))
    app.state.health_checker_task = health_checker_task
    logger.info("Background health checker started")
    
    yield
    
    # Cleanup: cancel the background task on shutdown
    if hasattr(app.state, 'health_checker_task'):
        app.state.health_checker_task.cancel()
        try:
            await app.state.health_checker_task
        except asyncio.CancelledError:
            logger.info("Background health checker stopped")

app = FastAPI(lifespan=lifespan)


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
