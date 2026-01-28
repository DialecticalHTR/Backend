from dishka import Provider, provide, Scope

from src.application.recognition.gateway import RecognitionGateway

from .settings import RecognitionTaskSettings
from .gateway import TaskiqRecognitionGateway


class RecognitionGatewayProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_settings(self) -> RecognitionTaskSettings:
        return RecognitionTaskSettings()  # type: ignore
    
    gateway = provide(
        provides=RecognitionGateway,
        source=TaskiqRecognitionGateway,
        scope=Scope.APP
    )
