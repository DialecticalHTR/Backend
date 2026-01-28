from events.integration.event import IntegrationEvent
from events.integration.topology import Topic


def get_event_topic(event: IntegrationEvent | type[IntegrationEvent]) -> Topic:
    topic_name = event.type.split(".")[0]
    return Topic(name=topic_name)
