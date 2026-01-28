from src.application.task.events import TaskStatusUpdatedV1
from src.application.bus import FanoutIntegrationEventBus
from src.infrastructure.messaging.utils import get_event_topic

from .base import IntegrationEventHandler

import logging
logger = logging.getLogger(__name__)


class TaskStatusUpdatedHandler(IntegrationEventHandler[TaskStatusUpdatedV1]):
    def __init__(
        self,
        bus: FanoutIntegrationEventBus
    ):
        self.bus = bus

    async def handle(self, event: TaskStatusUpdatedV1) -> None:
        await self.bus.send(
            topic=get_event_topic(event),
            event=event
        )
