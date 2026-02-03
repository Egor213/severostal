from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.http import configurate_routers
from src.app import init_container, init_logger
from src.database import Database
from src.metrics import configurate_metrics


@asynccontextmanager
async def lifespan(app: FastAPI):
    container = init_container()

    yield

    await container.resolve(Database).close()


def create_app() -> FastAPI:
    app = FastAPI(
        debug=True,
        title="TodoList",
        docs_url="/docs",
        lifespan=lifespan,
    )
    init_logger()
    configurate_routers(app)
    configurate_metrics(app)
    return app
