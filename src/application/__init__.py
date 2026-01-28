from dishka import Provider

from src.application.interactor.factory import InteractorFactoryProvider
from src.application.recognition.interactors import RecognitionInteractorsProvider
from src.application.task.interactors import TaskInteractorsProvider


def get_common_application_providers() -> list[Provider]:
    return [
        InteractorFactoryProvider()
    ]

