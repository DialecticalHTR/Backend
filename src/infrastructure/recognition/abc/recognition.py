import abc

import cv2

from ..utils import load_image


class TextRecognition(abc.ABC):
    async def recognise(self, img) -> str:
        image = load_image(img)
        if image is None:
            return ""
        return await self._recognise(image)

    @abc.abstractmethod
    async def _recognise(self, img: cv2.typing.MatLike) -> str:
        pass
