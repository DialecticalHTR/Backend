import logging
import signal
import asyncio

from dishka import AsyncContainer, Provider, Scope, make_async_container, provide, provide_all
from events.domain.implementation.dishka import DomainEventImplementationProvider

from src.application import get_common_application_providers
from src.application.bus import DurableIntegrationEventBus
from src.infrastructure import get_common_infrastructure_providers
from src.infrastructure.recognition_worker.broker import broker
from src.infrastructure.recognition_worker.provider import RecognitionGatewayProvider 

from .processor import OutboxProcessor
from .router import OutboxEventRouter
from .sender import (
    IntegrationBusOutboxEventSender,
    RecognitionGatewayOutboxEventSender
)

from src.logger import setup_logging
setup_logging()

logger = logging.getLogger(__package__)
logger.setLevel(logging.DEBUG)


class OutboxProvider(Provider):
    senders = provide_all(
        IntegrationBusOutboxEventSender,
        RecognitionGatewayOutboxEventSender,
        scope=Scope.APP
    )

    router = provide(
        OutboxEventRouter,
        scope=Scope.APP,
    )

    processor = provide(
        OutboxProcessor,
        scope=Scope.APP
    )


def create_container() -> AsyncContainer:
    return make_async_container(
        DomainEventImplementationProvider(),
        *get_common_application_providers(),
        *get_common_infrastructure_providers(),
        RecognitionGatewayProvider(),
        OutboxProvider(),
    )


async def startup_infrastructure(container: AsyncContainer) -> None:
    bus = await container.get(DurableIntegrationEventBus)
    
    await broker.startup()
    await bus.startup()


async def shutdown_infrastructure(container: AsyncContainer) -> None:
    bus = await container.get(DurableIntegrationEventBus)
    
    await bus.shutdown()
    await broker.shutdown()


async def main():
    stopping = asyncio.Event()

    def handler(*_):
        stopping.set()
    
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)

    container = create_container()    
    processor = await container.get(OutboxProcessor)

    await startup_infrastructure(container)
    await processor.startup()
    logger.info("Started outbox process")

    await stopping.wait()
    logger.info("Stopping outbox process...")

    await processor.shutdown()
    await shutdown_infrastructure(container)

    await container.close()
    logger.info("Stopped outbox process...")


if __name__ == "__main__":
    asyncio.run(main())
