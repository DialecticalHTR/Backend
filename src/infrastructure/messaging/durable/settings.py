from pydantic_settings import BaseSettings, SettingsConfigDict


class RabbitMQSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env.local', 
        env_prefix="INTEGRATION_RMQ_", 
        extra="ignore"
    )

    connection_url: str
