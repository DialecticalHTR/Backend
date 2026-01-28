from dishka import Provider, provide, Scope

from src.application.bus import FanoutIntegrationEventBus

from .bus import RedisFanoutIntegrationEventBus
from .settings import RedisBusSettings


class RedisFanoutIntegrationEventBusProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_settings(self) -> RedisBusSettings:
        return RedisBusSettings()  # type: ignore

    @provide(scope=Scope.APP)
    def provide_bus(self, settings: RedisBusSettings) -> FanoutIntegrationEventBus:
        return RedisFanoutIntegrationEventBus(
            redis_url=settings.url
        )
