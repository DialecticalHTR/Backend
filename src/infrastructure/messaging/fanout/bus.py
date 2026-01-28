import json
import asyncio
import logging

import redis.asyncio as redis
from events.integration.event import IntegrationEvent
from events.integration.topology import IntegrationEventBusRegistration, Topic

from src.application.bus import FanoutIntegrationEventBus


logger = logging.getLogger(__name__)


class RedisFanoutIntegrationEventBus(FanoutIntegrationEventBus):
    def __init__(
        self, 
        redis_url: str,
        registrations: list[IntegrationEventBusRegistration] | None = None
    ) -> None:
        super().__init__(registrations)

        self.connection_pool = redis.BlockingConnectionPool.from_url(redis_url)

        self.listeners: list[asyncio.Task] = []
    
    async def startup(self) -> None:
        registrations = self.registrations.copy()
        for registration in registrations:
            await self._create_listener(registration)
        
        logger.info("Startup complete")
    
    async def register(self, registration: IntegrationEventBusRegistration) -> None:
        await super().register(registration)
        await self._create_listener(registration) 
    
    async def shutdown(self) -> None:
        for listener in self.listeners:
            listener.cancel()

    async def send(self, topic: Topic, event: IntegrationEvent) -> None:
        async with redis.Redis(connection_pool=self.connection_pool) as conn:
            data = json.dumps(event.to_dict()).encode("utf-8")
            await conn.publish(
                channel=topic.name,
                message=data
            )
            logger.debug(f"Sent {event}")

    async def _create_listener(
        self,
        registration: IntegrationEventBusRegistration
    ):
        started_listening = asyncio.Event()
        
        listener = asyncio.create_task(self._listen_for_messages(registration, started_listening))
        self.listeners.append(listener)

        await started_listening.wait()
        logger.debug(f"Listener created for {registration.consumer.name}")

    async def _listen_for_messages(
        self, 
        registration: IntegrationEventBusRegistration,
        started_listening: asyncio.Event
    ) -> None:
        async with redis.Redis(connection_pool=self.connection_pool) as conn:
            channel = conn.pubsub()
            await channel.subscribe(registration.topic.name)

            started_listening.set()

            async for message in channel.listen():
                if not message:
                    continue
                if message["type"] != "message":
                    continue

                payload = json.loads(message["data"].decode("utf-8"))
                event = IntegrationEvent.from_dict(payload)

                await registration.consumer.on_event(event)
