from pydantic_settings import BaseSettings, SettingsConfigDict


class SQLSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env.local', 
        env_prefix="SQL_", 
        extra="ignore"
    )

    connection_url: str
