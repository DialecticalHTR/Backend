from pydantic_settings import BaseSettings, SettingsConfigDict


class RecognitionTaskSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env.local",
        env_prefix="TASKS_",
        extra="ignore"
    )

    broker_url: str
    result_backend_url: str
    cancellation_state_holder_url: str
    cancellation_notifier_url: str
    deduplication_backend_url: str
