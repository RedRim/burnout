import logging

from app.celery import celery_app


logger = logging.getLogger(__name__)


@celery_app.task(name="app.common.sample_heartbeat")
def sample_heartbeat() -> str:
    """
    Простая Celery-задача для проверки работоспособности очереди.
    Записывает сообщение в логи и возвращает строку.
    """
    logger.info("Sample heartbeat task executed")
    return "ok"


