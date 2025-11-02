import torch
import asyncio
from utils.device import autodetect_device
from typing import Optional, List
from dataclasses import dataclass

@dataclass
class Worker:
    """A worker with a model loaded on a specific GPU."""
    gpu_id: int
    device: torch.device
    
    
class WorkerPool:
    
    def __init__(self, num_gpus: Optional[int] = None):
        
        if num_gpus is None:
            if autodetect_device() == 'cuda':
                self.num_gpus = torch.cuda.device_count()
            else:
                self.num_gpus = 1
                
        self.workers = List[Worker] = []
        self.available_workers: asyncio.Queue = asyncio.Queue()
        