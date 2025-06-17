# app/core/config.py

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """
    Konfigurasi aplikasi menggunakan Pydantic Settings.
    Variabel environment akan otomatis dimuat dari file .env atau environment variables.
    """
    
    # Database Configuration
    DATABASE_URL: str
    
    # Supabase Configuration
    SUPABASE_URL: str
    SUPABASE_KEY: str
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    
    # Security Configuration
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Azure Configuration
    AZURE_STORAGE_CONNECTION_STRING: str
    AZURE_STORAGE_CONTAINER_NAME: str = "lapak-images"
    
    # Gemini AI Configuration
    GEMINI_API_KEY: str
    
    # Tripay Configuration
    TRIPAY_API_URL: str
    TRIPAY_MERCHANT_CODE: str
    TRIPAY_API_KEY: str
    TRIPAY_PRIVATE_KEY: str
    
    class Config:
        env_file = ".env"

# Instance global untuk settings
settings = Settings() 