from dishka import Provider, Scope, provide_all
from events.domain import DomainEventHandler

from src.domain.task import (
    TaskStatusUpdated, TaskInitialized, TaskCancelled
)
from src.application.task.events import (
    TaskCancelledV1, TaskStatusUpdatedV1, TaskSubmittedV1
)
from src.infrastructure.outbox import Outbox


class TaskStatusUpdatedEventHandler(DomainEventHandler[TaskStatusUpdated]):
    def __init__(
        self,
        outbox: Outbox
    ) -> None:
        self.outbox = outbox

    async def handle(self, event: TaskStatusUpdated) -> None:
        await self.outbox.put(
            TaskStatusUpdatedV1(task_id=str(event.task.id))
        )


class TaskInitializedEventHandler(DomainEventHandler[TaskInitialized]):
    def __init__(
        self,
        outbox: Outbox
    ) -> None:
        self.outbox = outbox

    async def handle(self, event: TaskInitialized) -> None:
        await self.outbox.put(
            TaskSubmittedV1(task_id=str(event.task.id))
        )


class TaskCancelledEventHandler(DomainEventHandler[TaskCancelled]):
    def __init__(
        self,
        outbox: Outbox
    ):
        self.outbox = outbox

    async def handle(self, event: TaskCancelled) -> None:
        await self.outbox.put(
            TaskCancelledV1(task_id=str(event.task.id))
        )


class TaskDomainEventHandlerProvider(Provider):
    scope = Scope.REQUEST

    handlers = provide_all(
        TaskInitializedEventHandler,
        TaskCancelledEventHandler,
        TaskStatusUpdatedEventHandler
    )
