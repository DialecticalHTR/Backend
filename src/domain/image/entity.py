import uuid

import cv2
import numpy as np
from events.domain.aggregate import AggregateRoot


def is_image(data: bytes) -> bool:
    buffer = np.frombuffer(data, np.uint8)
    return cv2.imdecode(buffer, cv2.IMREAD_ANYCOLOR) is not None


class Image(AggregateRoot):
    def __init__(
        self, 
        id: uuid.UUID,
        data: bytes
    ):
        super().__init__()
        
        self.id = id

        if not is_image(data):
            raise Exception("Supplied data is not an image")
        self.data: bytes = data


__all__ = [
    "Image"
]
