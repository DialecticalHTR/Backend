import uuid
from typing import Union

from pydantic import BaseModel

from src.domain.task import (
    Task, TaskStatus,
    CreatedStatus, FailedStatus, CompletedStatus, CancelledStatus
)

class TaskStatusDTO(BaseModel):
    type: str


class CreatedStatusDTO(TaskStatusDTO):
    type: str = "created"


class CompletedStatusDTO(TaskStatusDTO):
    type: str = "completed"
    text: str


class FailedStatusDTO(TaskStatusDTO):
    type: str = "failed"
    error_text: str


class CancelledStatusDTO(TaskStatusDTO):
    type: str = "cancelled"


TaskStatusUnion = Union[
    CreatedStatusDTO,
    CompletedStatusDTO,
    FailedStatusDTO,
    CancelledStatusDTO,
]


class TaskSubscriptionDTO(BaseModel):
    id: uuid.UUID


class TaskDTO(BaseModel):
    id: uuid.UUID
    status: TaskStatusUnion


class TaskMapper:
    def __init__(self):
        pass

    @staticmethod
    def from_domain(task: Task) -> TaskDTO:
        return TaskDTO(
            id=task.id,
            status=TaskStatusMapper.from_domain(task.status)
        )


class TaskStatusMapper:
    def __init__(self):
        pass

    @staticmethod
    def from_domain(task_status: TaskStatus) -> TaskStatusUnion:
        match task_status:
            case CreatedStatus():
                return CreatedStatusDTO()
            case CompletedStatus():
                return CompletedStatusDTO(text=task_status.recognized_text)
            case FailedStatus():
                return FailedStatusDTO(error_text=str(task_status.error_text))
            case CancelledStatus():
                return CancelledStatusDTO()
            case _:
                raise Exception("Unknown status type")
