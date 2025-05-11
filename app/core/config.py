# app/core/config.py
import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Registry Information System API"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/registry_system")
    
    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Registry System
    REGISTRY_USERNAME: str = os.getenv("REGISTRY_USERNAME", "")
    REGISTRY_PASSWORD: str = os.getenv("REGISTRY_PASSWORD", "")
    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "./output")
    KEN_ALL_CSV_PATH: str = os.getenv("KEN_ALL_CSV_PATH", "./data/KEN_ALL.CSV")
    
    # Redis (for Celery)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    class Config:
        env_file = ".env"

settings = Settings()