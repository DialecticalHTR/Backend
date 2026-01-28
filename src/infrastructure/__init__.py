from dishka import Provider

from src.infrastructure.domain_event_handlers import get_infrastructure_domain_event_handler_providers
from src.infrastructure.messaging import get_messaging_providers
from src.infrastructure.persistence.provider import get_persistence_providers


def get_common_infrastructure_providers() -> list[Provider]:
    return [
        *get_messaging_providers(),
        *get_persistence_providers(),
        *get_infrastructure_domain_event_handler_providers(),
    ]
