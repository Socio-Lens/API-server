import argparse
import logging
import os
import asyncio
from routes.internal import background_health_checker
from utils.router import include_route_modules
from utils.worker import WorkerPool
from utils.config import Config
from utils.healthChecker import healthChecker
from utils.metrics import ResponseTimeTracker, ResponseTimeMiddleware
from fastapi import FastAPI, Request
from slowapi.errors import RateLimitExceeded
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware





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
    
    healthChecker.initialize_routes(app)
        
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
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# in prod remove these, hack to work during testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],       # Allow all HTTP methods
    allow_headers=["*"],       # Allow all headers
)

# Initialize response time tracker (single instance shared by middleware and routes)
response_tracker = ResponseTimeTracker()
app.state.response_tracker = response_tracker

# Add response time tracking middleware
# Note: This must be added after other middlewares to measure total response time
app.add_middleware(ResponseTimeMiddleware, tracker=response_tracker)



@app.get("/")
@limiter.limit("5/minute")
def root(request: Request):
    return {"status": "ok", "msg": "SocioLens ASGI server" }

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", args.host)
    port = int(os.getenv("PORT", args.port))
    
    logger.info(f"Starting web server on {host}:{port}")

    if args.debug:
        # Works only if the module name can be imported (e.g., app.py)
        module_name = os.path.splitext(os.path.basename(__file__))[0]
        uvicorn.run(f"{module_name}:app", host=host, port=port, reload=True)
    else:
        uvicorn.run(app, host=host, port=port, reload=False)
