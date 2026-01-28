from dishka import Provider

from .provider import RecognitionGatewayProvider


def get_recognition_queue_providers() -> list[Provider]:
    return [
        RecognitionGatewayProvider()
    ]
