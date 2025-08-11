from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://aiuser:password@localhost:5432/ai_provenance"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # API Keys (to be filled in .env)
    GOOGLE_CLOUD_PROJECT_ID: str = ""
    OPENAI_API_KEY: str = ""
    AZURE_CUSTOM_VISION_KEY: str = ""
    PINECONE_API_KEY: str = ""
    
    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    API_KEY: str = "dev-api-key"
    
    # API Configuration
    API_PORT: str = "8000"
    API_URL: str = "http://localhost:8000"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
