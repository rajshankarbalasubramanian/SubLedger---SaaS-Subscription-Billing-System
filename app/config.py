import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # If a DATABASE_URL env var exists (like inside Docker), use it. 
    # Otherwise, fall back to a local local SQLite file named subledger.db
    DATABASE_URL: str = "sqlite:///./subledger.db"
    ENV: str = "development"

    # Pydantic V2 configuration definition strategy
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
DATABASE_URL = settings.DATABASE_URL
