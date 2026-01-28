from dishka import Provider

from .task_events import TaskDomainEventHandlerProvider


def get_infrastructure_domain_event_handler_providers() -> list[Provider]:
    return [
        TaskDomainEventHandlerProvider(),
    ]
