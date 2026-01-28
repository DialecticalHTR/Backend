from dishka import Provider

from .fanout.provider import RedisFanoutIntegrationEventBusProvider
from .durable.provider import RabbitMQDurableIntegrationEventBusProvider


def get_messaging_providers() -> list[Provider]:
    return [
        RedisFanoutIntegrationEventBusProvider(),
        RabbitMQDurableIntegrationEventBusProvider()
    ]
