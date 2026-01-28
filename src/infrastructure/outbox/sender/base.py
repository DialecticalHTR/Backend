import abc

from events.integration.event import IntegrationEvent


class OutboxEventSender(abc.ABC):
    @abc.abstractmethod
    async def send(self, event: IntegrationEvent):
        ...
