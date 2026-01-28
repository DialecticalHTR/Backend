import logging

from dishka import AsyncContainer, Scope, Provider, provide

from .base import BaseInteractor


class InteractorFactory[I: BaseInteractor]:
    """Allows creation of an interactor in a non-request scope"""

    def __init__(
        self,
        interactor_type: type[I],
        container: AsyncContainer
    ):
        if container.scope == Scope.REQUEST:
            logging.warning("Container is already in request scope")
        
        self.container = container
        self.interactor_type = interactor_type

        self.request_container: AsyncContainer | None = None

    async def __aenter__(self) -> I:
        self.request_container = await self.container(scope=Scope.REQUEST).__aenter__()
        return await self.request_container.get(self.interactor_type)
    
    async def __aexit__(self, exc_type, exc, tb):
        if self.request_container is not None:
            await self.request_container.close(exc)


class InteractorFactoryProvider(Provider):
    scope = Scope.REQUEST

    @provide(scope=Scope.APP)
    async def get_interactor_factory[I: BaseInteractor](
        self,
        interactor_type: type[I],
        container: AsyncContainer
    ) -> InteractorFactory[I]:
        return InteractorFactory[I](interactor_type, container)
