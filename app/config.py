from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Environment
    ENVIRONMENT: str = "development"  # development, production
    
    # Database settings
    DATABASE_URL: str = "mysql+pymysql://root:Maheesha%40123@localhost:3306/newgrademate"
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 3306
    DATABASE_NAME: str = "newgrademate"
    DATABASE_USER: str = "root"
    DATABASE_PASSWORD: str = "Maheesha@123"
    
    # CORS settings - can be overridden by environment variable
    CORS_ORIGINS: str = "http://127.0.0.1:3000,http://localhost:3000,http://127.0.0.1:5173,http://localhost:5173,http://127.0.0.1:8080,http://localhost:8080,https://gradematelk.vercel.app,https://*.vercel.app"
    
    # Render specific settings
    RENDER_EXTERNAL_URL: str = ""  # Will be set by Render automatically
    
    @property
    def database_url(self) -> str:
        """Construct database URL from components"""
        if self.DATABASE_URL and self.DATABASE_URL != "mysql+pymysql://root:password@localhost:3306/newgrademate":
            return self.DATABASE_URL
        return f"mysql+pymysql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        origins = [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
        
        # Add Render URL if available
        if self.RENDER_EXTERNAL_URL:
            origins.append(self.RENDER_EXTERNAL_URL)
            
        # Add local development origins if in development
        if self.ENVIRONMENT == "development":
            if "http://127.0.0.1:3000" not in origins:
                origins.append("http://127.0.0.1:3000")
            if "http://localhost:3000" not in origins:
                origins.append("http://localhost:3000")
            if "http://127.0.0.1:5173" not in origins:
                origins.append("http://127.0.0.1:5173")
            if "http://localhost:5173" not in origins:
                origins.append("http://localhost:5173")
            if "http://127.0.0.1:8080" not in origins:
                origins.append("http://127.0.0.1:8080")
            if "http://localhost:8080" not in origins:
                origins.append("http://localhost:8080")
                
        return origins

    class Config:
        env_file = ".env"

settings = Settings()
