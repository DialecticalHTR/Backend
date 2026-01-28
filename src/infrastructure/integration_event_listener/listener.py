import logging
from dishka import AsyncContainer, Scope
from events.integration.event import IntegrationEvent
from events.integration.topology import IntegrationEventBusRegistration, Topic
from events.integration.topology.consumer import Consumer, EventHandlerConsumer

from src.application.bus import DurableIntegrationEventBus
from src.infrastructure.messaging.utils import get_event_topic

from .handlers.base import IntegrationEventHandler


logger = logging.getLogger(__name__)


class IntegrationEventListener:
    def __init__(
        self,
        container: AsyncContainer,
        durable_bus: DurableIntegrationEventBus
    ) -> None:
        self.container = container
        self.durable_bus = durable_bus
        
        self.consumer: Consumer | None = None
        self.handlers: dict[type[IntegrationEvent], set[type[IntegrationEventHandler]]] = {}
    
    def add_handler[E: IntegrationEvent](
        self,
        event_type: type[E],
        handler: type[IntegrationEventHandler[E]]
    ):
        registered = event_type in self.handlers
        if not registered:
            self.handlers[event_type] = set()
        self.handlers[event_type].add(handler)

    async def initialize(self) -> None:
        # Add auto-discovered event handlers
        for event_type, handlers in IntegrationEventHandler.handlers.items():
            for handler in handlers:
                self.add_handler(event_type, handler)

        # Build the consumer
        event_types = list(self.handlers.keys())
        self.consumer = EventHandlerConsumer(
            "tasks",
            {
                event_type: [self._create_event_callback(event_type),]
                for event_type in event_types
            }
        )

        # Figure out the topics to subscribe to
        topic_events: dict[Topic, list[type[IntegrationEvent]]] = {}
        
        for event_type in event_types:
            topic = get_event_topic(event_type)

            if topic not in topic_events:
                topic_events[topic] = []
            topic_events[topic].append(event_type)

        # Register bus topology
        for topic, event_types in topic_events.items():
            await self.durable_bus.register(
                IntegrationEventBusRegistration(
                    consumer=self.consumer,
                    topic=topic,
                    events=event_types
                )
            )

    def _create_event_callback(self, event_type: type[IntegrationEvent]):
        async def callback(event: IntegrationEvent):
            logger.debug(f"Received {event}")

            async with self.container(scope=Scope.REQUEST) as request_container:
                for handler_type in self.handlers[event_type]:
                    handler = await request_container.get(handler_type)
                    await handler.handle(event)

        return callback
