from fastapi.routing import APIRoute
from collections import deque
class HealthChecker:
    
    def __init__(self):
        self.SERVICES = {}
        self.STATUS_HISTORY = {}

        

    def initialize_routes(self, app):
        for route in app.routes:
            if isinstance(route, APIRoute):
                # skip internal routes
                if "internal" in route.tags:
                    continue

                routeData = {
                    "route": route.path,
                    "methods": list(route.methods),
                    "name": route.name,
                    "description": route.description,
                    "last_checked": None,
                    "status": "Not Ready"
                }
                
                self.STATUS_HISTORY[route.name] = deque(maxlen=90)
                self.SERVICES[route.name] = routeData

healthChecker = HealthChecker()

__all__ = ['healthChecker']