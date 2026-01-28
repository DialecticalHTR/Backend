from pathlib import Path

import cv2
import numpy as np


def bytes_to_image(b: bytes) -> np.ndarray:
    return cv2.imdecode(np.frombuffer(b, dtype=np.uint8), cv2.IMREAD_COLOR)


def clamp(_min, _max, value):
    return min(max(_min, value), _max)


def load_image(data: Path | bytes | cv2.Mat) -> cv2.typing.MatLike | None:
    match data:
        case Path():
            return cv2.imread(str(data))
        case bytes():
            return bytes_to_image(data)
        case np.ndarray() | cv2.Mat():
            return data
    return None
