from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # HolderScan API
    holderscan_api_key: str
    holderscan_base_url: str = "https://api.holderscan.com/v0"

    # Server
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # CORS
    frontend_url: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
