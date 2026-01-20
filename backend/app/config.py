from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # HolderScan API
    holderscan_api_key: str
    holderscan_base_url: str = "https://api.holderscan.com/v0"

    # Solscan API
    solscan_api_key: Optional[str] = None
    solscan_base_url: str = "https://pro-api.solscan.io/v2.0"

    # Server
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # CORS
    frontend_url: str = "http://localhost:3000"

    class Config:
        # Look for .env in current directory and parent directory
        env_file = [".env", "../.env"]
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    settings = Settings()
    # Debug: show if Solscan API key is loaded (first/last few chars only for security)
    if settings.solscan_api_key:
        key = settings.solscan_api_key
        print(f"Solscan API key loaded: {key[:10]}...{key[-10:]}")
    else:
        print("WARNING: Solscan API key not found!")
    return settings
