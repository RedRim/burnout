import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.common.router import base_router, task_stats_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    yield

app = FastAPI(lifespan=lifespan, root_path="/api")
app.include_router(base_router)
app.include_router(task_stats_router)