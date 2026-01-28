import abc

import cv2

from ..utils import load_image


class TextDetection(abc.ABC):
    async def detect(self, img) -> list[list]:
        image = load_image(img)
        if image is None:
            return []
        return await self._detect(image)

    @abc.abstractmethod
    async def _detect(self, img: cv2.typing.MatLike) -> list[list]:
        pass
