import torch
import logging


logger = logging.getLogger(__name__)

def autodetect_device():
    if torch.cuda.is_available():
        device_type = 'cuda'
    elif torch.backends.mps.is_available():
        device_type = 'mps'
    else:
        device_type = 'cpu'
        
    logger.info(f"Autodetected device type as {device_type}")
        
    