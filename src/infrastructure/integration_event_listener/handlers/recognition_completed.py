import uuid

from src.application.recognition.events import RecognitionFinishedV1
from src.application.task.interactors import CompleteTaskInteractor

from .base import IntegrationEventHandler


class RecognitionFinishedHandler(IntegrationEventHandler[RecognitionFinishedV1]):
    def __init__(
        self,
        complete_task: CompleteTaskInteractor
    ):
        self.complete_task = complete_task

    async def handle(self, event: RecognitionFinishedV1) -> None:
        await self.complete_task(
            uuid.UUID(event.task_id)
        )