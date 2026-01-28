from typing import Literal, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class YOLOSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env.local",
        env_prefix="YOLO_",
        extra="ignore"
    )

    model_path: Optional[str] = None


class TrOCRSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env.local",
        env_prefix="TROCR_",
        extra="ignore"
    )

    model_type: Literal["pytorch", "onnx"]
    model_id: Optional[str] = None
