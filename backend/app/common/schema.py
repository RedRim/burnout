from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel


class CeleryTaskStatus(str, Enum):
    PENDING = "PENDING"
    STARTED = "STARTED"
    RETRY = "RETRY"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


class CeleryResponse(BaseModel):
    task_id: str
    status: CeleryTaskStatus


class CeleryResponseTaskStatus(BaseModel):
    task_id: str
    status: CeleryTaskStatus
    result: Optional[Any] = None


