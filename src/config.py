import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class Config:

    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    
    # Firebase
    FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")
    
    # Configuración del Modelo
    MODEL_NAME = "claude-sonnet-4-20250514"
    MAX_TOKENS = 4096
    TEMPERATURE = 0.7
    
    # Configuración de la aplicación
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Prompts
    PROMPTS_DIR = Path(__file__).parent / "prompts"
    
    @classmethod
    def validate(cls):
        """Valida que todas las configuraciones necesarias estén presentes"""
        if not cls.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY no está configurada")
        if not cls.FIREBASE_PROJECT_ID:
            raise ValueError("FIREBASE_PROJECT_ID no está configurado")
