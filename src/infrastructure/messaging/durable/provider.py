from typing import AsyncIterable

from dishka import Provider, provide, Scope
import aio_pika
from aio_pika.abc import AbstractRobustConnection

from src.application.bus import DurableIntegrationEventBus
from src.infrastructure.messaging.durable.bus import RabbitMQDurableIntegrationEventBus

from .settings import RabbitMQSettings


class RabbitMQDurableIntegrationEventBusProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_settings(self) -> RabbitMQSettings:
        return RabbitMQSettings() # type: ignore
    
    @provide(scope=Scope.APP)
    async def provide_robust_connection(
        self, settings: RabbitMQSettings
    ) -> AsyncIterable[AbstractRobustConnection]:
        connection = await aio_pika.connect_robust(
            url=settings.connection_url
        )
        yield connection
        await connection.close()

    @provide(scope=Scope.APP)
    def provide_bus(self, connection: AbstractRobustConnection) -> DurableIntegrationEventBus:
        return RabbitMQDurableIntegrationEventBus(
            connection
        )
