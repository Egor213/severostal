from fastapi import FastAPI
from fastapi.routing import APIRouter
from prometheus_fastapi_instrumentator import Instrumentator

from src.api.http.auth import router as auth_handlers_router
from src.api.http.health_check import router as health_check_router
from src.api.http.tasks import router as tasks_router


def configurate_routers(app: FastAPI):

    Instrumentator().instrument(app).expose(
        app,
        endpoint="/metrics",
        include_in_schema=True,
    )

    api_router = APIRouter(prefix="/api/v1")
    api_router.include_router(tasks_router)

    auth_router = APIRouter(prefix="/auth")
    auth_router.include_router(auth_handlers_router)

    app.include_router(api_router)
    app.include_router(auth_router)
    app.include_router(health_check_router)
