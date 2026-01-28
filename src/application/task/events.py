from dataclasses import dataclass

from events.integration.event import IntegrationEvent


@dataclass
class TaskSubmittedV1(IntegrationEvent):
    type = "task.submitted"
    version = 1

    task_id: str


@dataclass
class TaskCancelledV1(IntegrationEvent):
    type = "task.cancelled"
    version = 1

    task_id: str


@dataclass
class TaskStatusUpdatedV1(IntegrationEvent):
    type = "task.status_updated"
    version = 1
    
    task_id: str

    def __repr__(self) -> str:
        return f"TaskStatusUpdatedEvent({self.task_id!s})"


__all__ = [
    "TaskSubmittedV1",
    "TaskCancelledV1",
    "TaskStatusUpdatedV1",
]
