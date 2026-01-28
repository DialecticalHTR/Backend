from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisBusSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="INTEGRATION_REDIS_",
        env_file=".env.local",
        extra="ignore"
    )

    url: str
