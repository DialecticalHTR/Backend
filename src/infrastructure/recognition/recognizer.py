import logging

from src.domain.image import Image
from src.domain.recognizer import Recognizer

from .abc.detection import TextDetection
from .abc.recognition import TextRecognition
from .utils import bytes_to_image
from .grouping import boxes_to_groups


logger = logging.getLogger(__name__)


class MLRecognizer(Recognizer):
    def __init__(self, detector: TextDetection, recognizer: TextRecognition):
        self.detector = detector
        self.recognizer = recognizer

    async def recognize(self, image: Image) -> str:
        cv2_image = bytes_to_image(image.data)

        boxes = await self.detector.detect(cv2_image)
        groups = boxes_to_groups(boxes)
        
        lines = []
        for group in groups:
            words = []

            for box in group:
                x1, y1, x2, y2 = map(int, box)
                subimage = cv2_image[y1:y2, x1:x2]
                
                logger.debug(f"Recognizing image {box}...")
                text = await self.recognizer.recognise(subimage)
                
                words.append(text)
            line = ' '.join(words)
            lines.append(line)
        
        result = '\n'.join(lines)
        return result


class FakeRecognizer(Recognizer):
    async def recognize(self, _: Image) -> str:
        return "Fake text"
