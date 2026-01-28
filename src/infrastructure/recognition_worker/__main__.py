from dishka import AsyncContainer, make_async_container
from dishka.integrations.taskiq import setup_dishka
from taskiq import TaskiqEvents, TaskiqState
from taskiq.acks import AcknowledgeType
from taskiq.cli.worker.run import run_worker
from taskiq.cli.worker.args import WorkerArgs
from events.domain.implementation.dishka import DomainEventImplementationProvider

from src.application.bus import DurableIntegrationEventBus

from src.application import get_common_application_providers
from src.application.recognition.interactors import RecognitionInteractorsProvider
from src.infrastructure import get_common_infrastructure_providers

from src.infrastructure.recognition import get_recognition_providers
from src.infrastructure.recognition_worker.broker import broker


def create_container() -> AsyncContainer:
    return make_async_container(
        DomainEventImplementationProvider(),
        *get_common_application_providers(),
        RecognitionInteractorsProvider(),
        *get_common_infrastructure_providers(),
        *get_recognition_providers()
    )


@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def add_container_to_state(state: TaskiqState):
    state.container = create_container()
    setup_dishka(state.container, broker)

    integration_bus = await state.container.get(DurableIntegrationEventBus)
    await integration_bus.startup()


@broker.on_event(TaskiqEvents.WORKER_SHUTDOWN)
async def remove_container_from_state(state: TaskiqState):
    integration_bus = await state.container.get(DurableIntegrationEventBus)
    await integration_bus.shutdown()

    await state.container.close()


def main():
    from src.logger import setup_logging
    setup_logging()
    
    args = WorkerArgs(
        broker="src.infrastructure.recognition_worker.__main__:broker",
        modules=[],
        workers=1,
        max_prefetch=1,
        ack_type=AcknowledgeType.WHEN_SAVED,
        receiver="src.infrastructure.recognition_worker.receiver:RaisingReceiver"
    )
    run_worker(args)
    

if __name__ == "__main__":
    main()
