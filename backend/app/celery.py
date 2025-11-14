import os

import celery
from celery.schedules import crontab
from pydantic_settings import BaseSettings


class CeleryConfig(BaseSettings):
    broker_url: str
    result_backend: str
    DEFAULT_CELERY_QUEUE: str
    MAPS_SERVICE_WELLBORES_URL: str


def get_settings_celery() -> CeleryConfig:
    return CeleryConfig(
        broker_url=os.getenv("CELERY_BROKER_URL", ""),
        result_backend=os.getenv("CELERY_RESULT_BACKEND", ""),
        DEFAULT_CELERY_QUEUE=os.getenv("DEFAULT_CELERY_QUEUE", ""),
        MAPS_SERVICE_WELLBORES_URL=os.getenv("MAPS_SERVICE_WELLBORES_URL", ""),
    )


celery_config = get_settings_celery()

celery_app = celery.Celery(
    "src.app.config",
    broker=celery_config.broker_url,
    backend=celery_config.result_backend,
    broker_connection_retry_on_startup=False,
)

celery_app.conf.timezone = "Asia/Novosibirsk"
celery_app.conf.enable_utc = True


celery_app.autodiscover_tasks(
    [
        "app.common",
    ]
)

celery_app.conf.beat_schedule = {
    "sample_heartbeat_task": {
        "task": "app.common.sample_heartbeat",
        "schedule": crontab(minute="*/5"),  # каждые 5 минут
    },
}


