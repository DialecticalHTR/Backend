import abc
from typing import Type, get_origin, get_args

from events.integration.event import IntegrationEvent

# from src.framework.integration import IntegrationEvent


type IntegrationEventRegistry = dict[
    Type[IntegrationEvent], list[ Type[IntegrationEventHandler] ]
]


class IntegrationEventHandler[E: IntegrationEvent](abc.ABC):
    handlers: IntegrationEventRegistry = {}

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)

        for base in cls.__orig_bases__: # pyright: ignore[reportAttributeAccessIssue], liar
            origin = get_origin(base)
            if origin is IntegrationEventHandler:
                templates = get_args(base)
                domain_cls = templates[0]

                if issubclass(domain_cls, IntegrationEvent):
                    IntegrationEventHandler.__add_handler(domain_cls, cls)
    
    @staticmethod
    def __add_handler(event_cls, handler_cls):
        if event_cls not in IntegrationEventHandler.handlers:
            IntegrationEventHandler.handlers[event_cls] = []
        IntegrationEventHandler.handlers[event_cls].append(handler_cls)

    @abc.abstractmethod
    async def handle(self, event: E) -> None:
        ...

    async def __call__(self, event: E) -> None:
        await self.handle(event)
    