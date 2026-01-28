from events.integration.event import IntegrationEvent

from src.application.recognition.gateway import RecognitionGateway
from src.application.task.events import TaskCancelledV1, TaskSubmittedV1
from src.infrastructure.outbox.sender.base import OutboxEventSender


class RecognitionGatewayOutboxEventSender(OutboxEventSender):
    def __init__(
        self,
        gateway: RecognitionGateway
    ):
        self.gateway = gateway

    async def send(self, event: IntegrationEvent):
        match event:
            case TaskSubmittedV1():
                await self.gateway.submit_task(event.task_id)
            case TaskCancelledV1():
                await self.gateway.cancel_task(event.task_id)
            case _:
                raise ValueError("Unknown event type for recognition gateway sender")
