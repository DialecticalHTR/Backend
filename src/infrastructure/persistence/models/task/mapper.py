import uuid

from src.domain.task import Task
from src.domain.task.status import (
    TaskStatus,
    UninitializedStatus,
    CreatedStatus,
    CompletedStatus,
    FailedStatus,
    CancelledStatus,
    QueuedStatus
)

from .model import (
    TaskModel,
    TaskStatusModel,
    UninitializedStatusModel,
    CreatedStatusModel,
    CompletedStatusModel,
    FailedStatusModel,
    CancelledStatusModel,
    QueuedStatusModel
)


class TaskMapper:
    @staticmethod
    async def from_domain(task: Task) -> TaskModel:
        return TaskModel(
            id=str(task.id),
            image_id=str(task.image_id),
            status=await TaskStatusMapper.from_domain(task.status)
        )

    @staticmethod
    async def to_domain(model: TaskModel) -> Task:
        return Task(
            id=uuid.UUID(model.id),
            image_id=uuid.UUID(model.image_id),
            status=await TaskStatusMapper.to_domain(await model.awaitable_attrs.status)
        )


class TaskStatusMapper:
    @staticmethod
    async def from_domain(status: TaskStatus) -> TaskStatusModel:
        match status:
            case UninitializedStatus():
                return UninitializedStatusModel()
            case CreatedStatus():
                return CreatedStatusModel()
            case QueuedStatus():
                return QueuedStatusModel()
            case CancelledStatus():
                return CancelledStatusModel()
            case CompletedStatus():
                return CompletedStatusModel(text=status.recognized_text)
            case FailedStatus():
                return FailedStatusModel(
                    # error_code=status.error_code,
                    error_text=status.error_text
                )
            case _:
                raise Exception("Unknown task status type")

    @staticmethod
    async def to_domain(model: TaskStatusModel) -> TaskStatus:
        match model:
            case UninitializedStatusModel() | None:
                return UninitializedStatus()
            case CreatedStatusModel():
                return CreatedStatus()
            case QueuedStatusModel():
                return QueuedStatus()
            case CancelledStatusModel():
                return CancelledStatus()
            case CompletedStatusModel():
                return CompletedStatus(recognized_text=await model.awaitable_attrs.text)
            case FailedStatusModel():
                return FailedStatus(
                    # error_code=model.error_code,
                    error_text=await model.awaitable_attrs.error_text
                )
            case _:
                raise Exception("Unknown task status model type")