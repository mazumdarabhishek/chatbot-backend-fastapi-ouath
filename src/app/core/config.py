from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI

import os
from pathlib import Path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    access_token_expire_days: int = 30
    otp_cooldown_period_seconds: int = 30
    otp_length : int = 6
    
    email_from: str
    app_password: str
    email_port: int
    email_host: str
    
    app_name: str = "Chatbot FastAPI"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: str = "app.log"
    logs_directory: str = "logs"
    log_level: str = "INFO"
    
    company_name: str = "WannaBeAIops"
    
    gemini_api_key: str
    gemini_model: str = "gemini-flash-latest"
    

    model_config = {
        "env_file": str(PROJECT_ROOT / ".env"),
        "case_sensitive": True,
        "extra": "ignore"
    }


settings = Settings()


def get_model():
    return ChatGoogleGenerativeAI(model=settings.gemini_model, api_key=settings.gemini_api_key)