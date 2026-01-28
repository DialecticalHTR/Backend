from dishka import Provider

from .provider import MLRecognizerProvider
from .implemenation.detection import YOLOTextDetectionProvider
from .implemenation.recognition import TrOCRTextRecognitionProvider


def get_recognition_providers() -> list[Provider]:
    return [
        YOLOTextDetectionProvider(),
        TrOCRTextRecognitionProvider(),
        MLRecognizerProvider()
    ]
