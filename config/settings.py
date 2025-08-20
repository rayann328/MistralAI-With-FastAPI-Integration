import os
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    app_name: str = "Cultural Assistant API"
    app_version: str = "1.0.0"
    mistral_model: str = "mistral-tiny"
    history_size: int = 6
    request_timeout: int = 30
    max_request_size: int = 1024  # 1KB
    rate_limit_per_minute: int = 10
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()# settings.py
"""
This is the settings.py file
"""

