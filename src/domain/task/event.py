import typing

from events.domain.event import DomainEvent
# from src.framework.domain import DomainEvent

from .status import TaskStatus

if typing.TYPE_CHECKING:
    from .entity import Task


class TaskInitialized(DomainEvent):
    type: str = "task:initialized" # type: ignore

    def __init__(self, task: "Task"):
        self.task = task


class TaskCancelled(DomainEvent):
    type: str = "task:cancelled" # type: ignore

    def __init__(self, task: "Task"):
        self.task = task


class TaskFinished(DomainEvent):
    type: str = "task:finished" # type: ignore

    def __init__(self, task: "Task"):
        self.task = task


class TaskCompleted(DomainEvent):
    type: str = "task:completed" # type: ignore

    def __init__(self, task: "Task", text: str):
        self.task = task
        self.text = text


class TaskFailed(DomainEvent):
    type: str = "task:failed" # type: ignore

    def __init__(
        self, 
        task: "Task", 
        # error_code: FailedStatus.ErrorCode,
        error_text: typing.Optional[str]
    ):
        self.task = task
        # self.error_code = error_code
        self.error_text = error_text


class TaskStatusUpdated(DomainEvent):
    type: str = "task:status_updated" # type: ignore

    def __init__(
        self, 
        task: "Task", 
        task_status: TaskStatus
    ):
        self.task = task
        self.task_status = task_status


__all__ = [
    "TaskInitialized",
    "TaskCancelled",
    "TaskFinished",
    "TaskCompleted",
    "TaskFailed",
    "TaskStatusUpdated"
]
