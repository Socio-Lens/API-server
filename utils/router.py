import importlib
import pkgutil
import logging
from fastapi import APIRouter, FastAPI


def include_route_modules(app: FastAPI, package_name: str = "routes"):
    """
    Import modules in the package and include routers named `router`.

    """
    logger = logging.getLogger(__name__)
    package = importlib.import_module(package_name)
    package_path = package.__path__  # needed for pkgutil.iter_modules

    for finder, name, ispkg in pkgutil.iter_modules(package_path):
        full_name = f"{package_name}.{name}"
        try:
            module = importlib.import_module(full_name)
            # Try common router names
            candidates = []
            if hasattr(module, "router"):
                candidates.append(module.router)
            # fallback: find any APIRouter in module globals
            if not candidates:
                for val in module.__dict__.values():
                    if isinstance(val, APIRouter):
                        candidates.append(val)
                        break

            for r in candidates:
                if isinstance(r, APIRouter):
                    app.include_router(r)
                    logger.info(f"Included router from {full_name} (prefix={getattr(r, 'prefix', None)})")
                else:
                    logger.debug(f"Found object named router in {full_name} but it's not APIRouter")
        except Exception as e:
            logger.exception(f"Failed to include routes from {full_name}: {e}")
