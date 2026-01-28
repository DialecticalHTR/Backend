from fastapi.routing import APIRouter

from .health import router as health
from .task import router as task


routers: list[APIRouter] = [
    health, task
]

__all__ = [
    "routers"
]