import abc
import uuid

from .entity import Image


class ImageRepository(abc.ABC):
    @abc.abstractmethod
    async def update(self, image: Image):
        pass

    @abc.abstractmethod
    async def delete_by_id(self, image_id: uuid.UUID):
        pass

    @abc.abstractmethod
    async def get_by_id(self, image_id: uuid.UUID) -> Image:
        pass
