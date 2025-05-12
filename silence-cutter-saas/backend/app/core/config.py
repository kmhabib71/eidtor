from pydantic_settings import BaseSettings
import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "Silence Cutter"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-for-development-only")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    ALGORITHM: str = "HS256"
    
    # CORS
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # MongoDB settings
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "silence_cutter")
    
    # Storage settings
    STORAGE_TYPE: str = os.getenv("STORAGE_TYPE", "local")  # "local", "s3", or "gcs"
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", "silence-cutter")
    S3_REGION: str = os.getenv("S3_REGION", "us-east-1")
    GCS_BUCKET_NAME: str = os.getenv("GCS_BUCKET_NAME", "silence-cutter")
    
    # File storage
    STATIC_FILES_DIR: str = os.getenv("STATIC_FILES_DIR", "static")
    TEMP_DIR: str = os.getenv("TEMP_DIR", "temp")
    UPLOAD_DIR: str = os.path.join(STATIC_FILES_DIR, "uploads")
    PROCESSED_DIR: str = os.path.join(STATIC_FILES_DIR, "processed")
    
    # Processing settings
    MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "500"))
    SILENCE_THRESHOLD_DB: float = float(os.getenv("SILENCE_THRESHOLD_DB", "-40"))
    MIN_SILENCE_DURATION_MS: int = int(os.getenv("MIN_SILENCE_DURATION_MS", "500"))
    
    # Redis for Celery
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Payment
    STRIPE_API_KEY: str = os.getenv("STRIPE_API_KEY", "")
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

settings = Settings() 