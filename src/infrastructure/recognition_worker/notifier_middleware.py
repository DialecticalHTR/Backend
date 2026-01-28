from typing import Any

from taskiq import TaskiqMessage, TaskiqMiddleware, TaskiqResult, AsyncTaskiqDecoratedTask

from src.application.bus import DurableIntegrationEventBus
from src.application.recognition.events import RecognitionFinishedV1
from src.infrastructure.messaging.utils import get_event_topic


class ResultNotifierMiddleware(TaskiqMiddleware):
    def __init__(self) -> None:
        super().__init__()

        self.registered_task_names: list[str] = []

    def register(self, task: AsyncTaskiqDecoratedTask):
        self.registered_task_names.append(task.task_name)

    async def post_save(
        self, message: TaskiqMessage, result: TaskiqResult[Any]
    ):
        bus = await self.broker.state.container.get(DurableIntegrationEventBus)
        await bus.send(
            topic=get_event_topic(RecognitionFinishedV1),
            event=RecognitionFinishedV1(
                task_id=message.task_id
            )
        )
