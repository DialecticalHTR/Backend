from dishka import Provider, provide, Scope

from src.domain.recognizer import Recognizer

from .recognizer import MLRecognizer


class MLRecognizerProvider(Provider):
    recognizer = provide(
        provides=Recognizer,
        source=MLRecognizer,
        scope=Scope.APP
    )
