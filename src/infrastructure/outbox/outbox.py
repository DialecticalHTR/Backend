import abc
from typing import Iterable, Protocol

from events.integration.event import IntegrationEvent


class OutboxItem(abc.ABC):
    def __init__(self, event: IntegrationEvent) -> None:
        self.event = event
    
    @abc.abstractmethod
    async def mark_as_processed(self) -> None:
        ...


class Outbox(Protocol):
    @abc.abstractmethod
    async def put(self, event: IntegrationEvent) -> None:
        ...
    
    @abc.abstractmethod
    async def get_batch(self, batch_size: int) -> Iterable[OutboxItem]:
        ...
