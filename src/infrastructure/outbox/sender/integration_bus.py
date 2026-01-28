from events.integration.event import IntegrationEvent

from src.application.bus import DurableIntegrationEventBus
from src.infrastructure.messaging.utils import get_event_topic
from src.infrastructure.outbox.sender.base import OutboxEventSender


class IntegrationBusOutboxEventSender(OutboxEventSender):
    def __init__(
        self,
        bus: DurableIntegrationEventBus
    ):
        self.bus = bus

    async def send(self, event: IntegrationEvent):
        await self.bus.send(
            topic=get_event_topic(event),
            event=event
        )
