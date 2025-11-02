import argparse
import logging
from fastapi import FastAPI, HTTPException, Request

parser = argparse.ArgumentParser(description='SocioLens Web Server')
parser.add_argument('-n', '--num-gpus', type=int, default=1, help='Number of GPUs to use (default: 1)')
parser.add_argument('-p', '--port', type=int, default=8000, help='Port to run the server on')
parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind the server to')
args = parser.parse_args()

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


app = FastAPI()


@app.get("/")
def root(request: Request):
    logger.debug(request)
    return {"status": "ok", "msg": "SocioLens ASGI server" }

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting web server on {args.host}:{args.port}")
    
    uvicorn.run(app, host=args.host, port=args.port)
