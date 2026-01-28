from ast import Import
import asyncio
import logging

import cv2
from dishka import Provider, provide, Scope

from .settings import TrOCRSettings
from ..abc.recognition import TextRecognition


logger = logging.getLogger(__name__)


class PyTorchTrOCRTextRecognition(TextRecognition):
    def __init__(self, model: str):
        try:
            import torch
            from transformers import PreTrainedModel
            from transformers import TrOCRProcessor, VisionEncoderDecoderModel
        except ImportError as e:
            logger.fatal(
                "PyTorchTrOCRTextRecognition requires torch and transformers to be installed.\n"
                "Install cpu and gpu extra to get inference modules.",
                exc_info=e
            )
            raise
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device {self.device}")

        self.processor = TrOCRProcessor.from_pretrained(model)
        
        self.model: PreTrainedModel = VisionEncoderDecoderModel.from_pretrained(model).to(self.device)
        self.model.eval()

    async def _recognise(self, img: cv2.typing.MatLike) -> str:
        if self.device.type == "cpu":
            # Send to new thread to not block the main one when using a CPU
            # https://discuss.pytorch.org/t/using-asyncio-while-waiting-on-gpu/84928/9
            task = asyncio.create_task(await asyncio.to_thread(self._run_trocr, img))
            return await task
        else:
            # CUDA and other backends release GIL
            return await self._run_trocr(img)

    async def _run_trocr(self, img: cv2.typing.MatLike) -> str:
        pixel_values = self.processor(img, return_tensors="pt").pixel_values.to(self.device)
        generated_ids = self.model.generate(pixel_values)
        generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return generated_text


class ONNXTrOCRTextRecognition(TextRecognition):
    def __init__(self, model: str):
        try:
            import torch
            from transformers import TrOCRProcessor
            from optimum.onnxruntime import ORTModelForVision2Seq
        except ImportError as e:
            logger.fatal(
                f"ONNXTrOCRTextRecognition requires torch, transformers and optimum.onnxruntime to "
                "be installed.\nInstall cpu and gpu extra to get inference modules.",
                exc_info=e
            )
            raise
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device {self.device}")

        self.processor = TrOCRProcessor.from_pretrained(model)
        self.model = ORTModelForVision2Seq.from_pretrained(
            model,         
            encoder_file_name="encoder_model.onnx",
            decoder_file_name="decoder_model.onnx"
        ).to(self.device)

    async def _recognise(self, img: cv2.typing.MatLike) -> str:
        task = asyncio.create_task(await asyncio.to_thread(self._run_trocr, img))
        return await task

    async def _run_trocr(self, img: cv2.typing.MatLike) -> str:
        pixel_values = self.processor(img, return_tensors="pt").pixel_values.to(self.device)
        generated_ids = self.model.generate(pixel_values)
        generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return generated_text


class TrOCRTextRecognitionProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_settings(self) -> TrOCRSettings:
        return TrOCRSettings() # type: ignore

    @provide(scope=Scope.APP)
    def provide_pytorch_recognition(self, settings: TrOCRSettings)-> TextRecognition:
        match settings.model_type:
            case "pytorch":
                return PyTorchTrOCRTextRecognition(
                    settings.model_id or "Daniil-Domino/trocr-base-ru-dialectic-stackmix"
                )
            case "onnx":
                return ONNXTrOCRTextRecognition(
                    settings.model_id or "CherryJam/trocr-base-ru-dialectic-stackmix-onnx"
                )
