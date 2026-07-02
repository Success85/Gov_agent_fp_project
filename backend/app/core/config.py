from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Gov Agent"
    environment: str = "development"
    database_url: str = "postgresql+psycopg://gov_agent:gov_agent@db:5432/gov_agent"
    cors_origins: list[str] = ["*"]
    storage_dir: str = "storage"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
