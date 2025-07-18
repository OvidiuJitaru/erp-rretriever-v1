import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings using Pydantic
    Automatically loads from environment variables or .env file
    """

    # API Settings
    app_name: str = "Agent Assistant"
    app_version: str = "1.0.0"
    debug: bool = True

    # MongoDB Settings
    mongo_uri: str = "localhost"
    mongo_db_history: str = "history"

    embedder: str = "ArchitRastogi/bert-base-italian-embeddings"
    # CORS Settings
    # allowed_origins: list = ["http://localhost:3000"]

    llm_api_url: str = "0.0.0.0"

    # SQL SERVER settings
    db_server: str = "sage"
    db_database: str = "x3"
    db_username: str = "root"
    db_password: str = "<PASSWORD>"

    class Config:
        # Loads from .env file if present
        env_file = "local.env"
        case_sensitive = False

# Create global settings instance
settings = Settings()