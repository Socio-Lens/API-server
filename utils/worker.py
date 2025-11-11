import os
import torch
import asyncio
import logging
from utils.config import Config
from utils.device import autodetect_device
from typing import Optional, List
from dataclasses import dataclass
from pydantic import BaseModel
from transformers import logging as hf_logging
from transformers import AutoTokenizer, AutoModelForSequenceClassification


logger = logging.getLogger(__name__)

hf_logging.set_verbosity(50)

@dataclass
class Worker:
    """A worker with a model loaded on a specific GPU."""
    gpu_id: int
    device: torch.device
    tokenizer: object
    model: object
    
    
class WorkerPool:
    
    def __init__(self, num_gpus: Optional[int] = None):
        
        self.device_type = autodetect_device()
        if num_gpus is None:
            if self.device_type == 'cuda':
                self.num_gpus = torch.cuda.device_count()
            else:
                self.num_gpus = 1
                
        self.workers: List[Worker] = []
        self.available_workers: asyncio.Queue = asyncio.Queue()
        

    async def initialize(self, config: Config):
        SAVE_DIR = f"{config.model_dir}/pretrained"
        if os.path.exists(SAVE_DIR):
            logger.info("Model exists locally, skipping download")
        else:
            tokenizer = AutoTokenizer.from_pretrained(config.model_name)
            model = AutoModelForSequenceClassification.from_pretrained(config.model_name)

            model.save_pretrained(SAVE_DIR)
            tokenizer.save_pretrained(SAVE_DIR)

            logger.info(f"Saved pretrained model to {SAVE_DIR}")

        logger.info(f"Initializing worker pool with {self.num_gpus} GPUs...")
        if self.num_gpus > 1:
            assert self.device_type == "cuda", "Only CUDA supports multiple workers/GPUs. cpu|mps does not."

        
        for gpu_id in range(self.num_gpus):
            if self.device_type == "cuda":
                device = torch.device(f"cuda:{gpu_id}")
                logger.info(f"Loading model on GPU {gpu_id}")
            else:
                device = torch.device(self.device_type)
                logger.info(f"Loading model on {self.device_type}")

            
            tokenizer = AutoTokenizer.from_pretrained(config.model_name)
            model = AutoModelForSequenceClassification.from_pretrained(config.model_name)
            model.to(device)
            model.eval()

            worker = Worker(
                gpu_id=gpu_id,
                device=device,
                model=model,
                tokenizer=tokenizer,
            )

            self.workers.append(worker)
            await self.available_workers.put(worker)

        logger.info(f"All {self.num_gpus} workers initialized")

    async def acquire_worker(self) -> Worker:
        return await self.available_workers.get()
    
    async def release_worker(self, worker: Worker):
        await self.available_workers.put(worker)