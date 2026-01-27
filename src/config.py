"""Configuration management for the application"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration"""

    # OpenAI/LLM Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4-turbo-preview")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))
    LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "2000"))

    # Data Processing Configuration
    MAX_PREVIEW_ROWS = int(os.getenv("MAX_PREVIEW_ROWS", "100"))
    SAMPLE_SIZE = int(os.getenv("SAMPLE_SIZE", "50"))
    MAX_TOKENS_FOR_SAMPLING = int(os.getenv("MAX_TOKENS_FOR_SAMPLING", "8000"))

    # Supported file types
    SUPPORTED_EXCEL_EXTENSIONS = [".xlsx", ".xls"]
    SUPPORTED_CSV_EXTENSIONS = [".csv"]

    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        if not cls.OPENAI_API_KEY:
            return False
        return True
