import abc

from .image import Image


class Recognizer(abc.ABC):
    @abc.abstractmethod
    async def recognize(self, image: Image) -> str:
        pass
