from fastapi import APIRouter
from celery.result import AsyncResult

from .schema import CeleryResponse, CeleryResponseTaskStatus
from .tasks import sample_heartbeat
from ..celery import celery_app

base_router = APIRouter(prefix="/base", tags=["base"])
task_stats_router = APIRouter(prefix="/tasks", tags=["tasks"])

@base_router.get("/foo")
async def foo() -> str:
    return "foo"

@base_router.post(
    "/heartbeat",
    response_model=CeleryResponse,
    summary="Запуск Celery heartbeat задачи вручную",
)
async def run_heartbeat_task() -> CeleryResponse:
    """
    Ручной запуск простой Celery-задачи.
    """
    task = sample_heartbeat.delay()
    return CeleryResponse(task_id=task.id, status=task.status)


@task_stats_router.get(
    "/{task_id}",
    response_model=CeleryResponseTaskStatus,
    summary="Получение статуса Celery-задачи",
)
async def get_task_status(task_id: str) -> CeleryResponseTaskStatus:
    """
    Возвращает статус Celery-задачи по её `task_id`.
    """
    result = AsyncResult(task_id, app=celery_app)
    # result.result может быть не сериализуемым, поэтому возвращаем только при успешном выполнении
    payload_result = result.result if result.successful() else None
    return CeleryResponseTaskStatus(
        task_id=task_id,
        status=result.status,
        result=payload_result,
    )
