from events.integration.event import IntegrationEvent

from src.application.task.events import TaskCancelledV1, TaskSubmittedV1

from .sender.integration_bus import IntegrationBusOutboxEventSender
from .sender.recognition_gateway import RecognitionGatewayOutboxEventSender


class OutboxEventRouter:
    def __init__(
        self,
        bus_sender: IntegrationBusOutboxEventSender,
        gateway_sender: RecognitionGatewayOutboxEventSender
    ):
        self.bus_sender = bus_sender
        self.gateway_sender = gateway_sender
    
    async def send(self, event: IntegrationEvent) -> None:
        if isinstance(
            event, (TaskSubmittedV1, TaskCancelledV1)
        ):
            await self.gateway_sender.send(event)
            return
        
        await self.bus_sender.send(event)
