from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class S3Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env.local", 
        env_prefix="S3_", 
        extra="ignore"
    )

    access_key: str
    secret_key: str
    session_token: Optional[str] = None

    endpoint_url: Optional[str] = None
    region_name: Optional[str] = None
