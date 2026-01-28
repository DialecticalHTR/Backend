from dishka import Provider, Scope, provide

from src.infrastructure.outbox.outbox import Outbox

from .outbox import SQLOutbox


class OutboxProvider(Provider):
    outbox = provide(
        source=SQLOutbox,
        provides=Outbox,
        scope=Scope.REQUEST
    )
