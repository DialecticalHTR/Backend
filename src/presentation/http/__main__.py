import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from dishka import make_async_container, AsyncContainer
from dishka.integrations.fastapi import setup_dishka as setup_fastapi
from events.domain.implementation.dishka import DomainEventImplementationProvider

from src.application.bus import DurableIntegrationEventBus, FanoutIntegrationEventBus

from src.application import get_common_application_providers
from src.application.task.interactors import TaskInteractorsProvider
from src.infrastructure import get_common_infrastructure_providers

from src.infrastructure.recognition_worker.provider import RecognitionGatewayProvider
from src.logger import setup_logging
setup_logging()

from .routers import routers


def create_container() -> AsyncContainer:
    return make_async_container(
        DomainEventImplementationProvider(),
        *get_common_application_providers(),
        TaskInteractorsProvider(),
        *get_common_infrastructure_providers(),
        # FIXME: split task interactors in a different providers
        RecognitionGatewayProvider()
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    container: AsyncContainer = app.state.dishka_container

    durable_bus = await container.get(DurableIntegrationEventBus)
    fanout_bus = await container.get(FanoutIntegrationEventBus)

    await fanout_bus.startup()
    await durable_bus.startup()

    yield

    await durable_bus.shutdown()
    await fanout_bus.shutdown()


def app() -> FastAPI:
    container = create_container()
    
    app = FastAPI(
        lifespan=lifespan
    )

    for router in routers:
        app.include_router(router)

    setup_fastapi(container, app)

    return app


if __name__ == "__main__":
    server = uvicorn.Server(
        uvicorn.Config(
            app=app, 
            host="0.0.0.0", 
            port=8000,
            log_level=logging.INFO
        )
    )
    server.run()
