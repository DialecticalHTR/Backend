import signal
import asyncio

from dishka import AsyncContainer, make_async_container, Provider, Scope, provide, provide_all
from dishka.integrations.taskiq import setup_dishka
from events.domain.implementation.dishka import DomainEventImplementationProvider

from src.application import get_common_application_providers
from src.application.task.interactors import TaskInteractorsProvider
from src.infrastructure import get_common_infrastructure_providers
from src.application.bus import DurableIntegrationEventBus, FanoutIntegrationEventBus
from src.infrastructure.recognition_worker.broker import broker
from src.infrastructure.recognition_worker.provider import RecognitionGatewayProvider

from .listener import IntegrationEventListener
from .handlers.task_status_updated import TaskStatusUpdatedHandler
from .handlers.recognition_completed import RecognitionFinishedHandler


class EventListenerProvider(Provider):
    handlers = provide_all(
        TaskStatusUpdatedHandler,
        RecognitionFinishedHandler,
        scope=Scope.REQUEST
    )
    
    listener = provide(
        IntegrationEventListener,
        scope=Scope.APP
    )


def create_container() -> AsyncContainer:
    return make_async_container(
        DomainEventImplementationProvider(),
        *get_common_application_providers(),
        TaskInteractorsProvider(),
        *get_common_infrastructure_providers(),
        RecognitionGatewayProvider(),
        EventListenerProvider(),
    )


async def define_integration_bus_topology(container: AsyncContainer):
    event_listener = await container.get(IntegrationEventListener)
    await event_listener.initialize()


async def startup_infrastructure(container: AsyncContainer):
    setup_dishka(container, broker)
    durable_bus = await container.get(DurableIntegrationEventBus)
    fanout_bus = await container.get(FanoutIntegrationEventBus)

    await broker.startup()       # Used in RecognitionGateway, a handler dependency
    await fanout_bus.startup()   # Fanout bus is a handler dependency
    await durable_bus.startup()  # Events are received from durable bus


async def shutdown_infrastructure(container: AsyncContainer):
    durable_bus = await container.get(DurableIntegrationEventBus)
    fanout_bus = await container.get(FanoutIntegrationEventBus)

    await durable_bus.shutdown()
    await fanout_bus.shutdown()
    await broker.shutdown()


async def main():
    cancel_requested = asyncio.Event()

    def app_closer(*_):
        cancel_requested.set()

    signal.signal(signal.SIGINT, app_closer)
    signal.signal(signal.SIGTERM, app_closer)

    container = create_container()

    await define_integration_bus_topology(container)
    await startup_infrastructure(container)

    await cancel_requested.wait()

    await shutdown_infrastructure(container)  
    await container.close()  


if __name__ == "__main__":
    from src.logger import setup_logging
    setup_logging()
    
    asyncio.run(main())
