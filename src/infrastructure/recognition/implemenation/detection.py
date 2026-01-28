import asyncio

import cv2
from ultralytics.models.yolo import YOLO
from dishka import Provider, Scope, provide

from src.infrastructure.recognition.implemenation.settings import YOLOSettings

from ..abc.detection import TextDetection
from ..utils import clamp


class YOLOTextDetection(TextDetection):
    def __init__(self, model: str):
        self.yolo = YOLO(model)

    async def _detect(self, img: cv2.typing.MatLike) -> list[list]:
        task = asyncio.create_task(await asyncio.to_thread(self._run_yolo, img))
        return await task

    async def _run_yolo(self, img: cv2.typing.MatLike) -> list[list]:
        result = self.yolo(img)[0]
        boxes = result.boxes.xyxy
        boxes = self._postprocess(boxes)
        return boxes

    def _postprocess(self, boxes: list[list]) -> list[list]:
        new_boxes = []
        for i, b1 in enumerate(boxes):
            for j, b2 in enumerate(boxes):
                if i == j:
                    continue

                x11, y11, x12, y12 = b1
                x21, y21, x22, y22 = b2
                # if x11 >= x21 and y11 >= y21 and x12 <= x22 and y12 <= y22:
                #     break
                
                x31 = clamp(x11, x12, x21)
                x32 = clamp(x11, x12, x22)
                y31 = clamp(y11, y12, y21)
                y32 = clamp(y11, y12, y22)

                area = (y32 - y31) * (x32 - x31)
                b1_area = (y12 - y11) * (x12 - x11)

                if area / b1_area > 0.9:
                    break
            else:
                new_boxes.append(b1)
        return new_boxes


class YOLOTextDetectionProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_settings(self) -> YOLOSettings:
        return YOLOSettings()  # type: ignore

    @provide(scope=Scope.APP)
    def provide_detection(self, settings: YOLOSettings) -> TextDetection:
        model_path = settings.model_path

        if model_path is None:
            from huggingface_hub import hf_hub_download
            model_path = hf_hub_download(
                repo_id="Daniil-Domino/yolo11x-dialectic", 
                filename="model.pt",
            )
        
        return YOLOTextDetection(model_path)
    