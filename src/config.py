"""Configuration management for the application"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration"""

    # OpenAI/LLM Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-5.2-2025-12-11")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))
    LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "2000"))

    # Data Processing Configuration
    MAX_PREVIEW_ROWS = int(os.getenv("MAX_PREVIEW_ROWS", "100"))
    SAMPLE_SIZE = int(os.getenv("SAMPLE_SIZE", "50"))
    MAX_TOKENS_FOR_SAMPLING = int(os.getenv("MAX_TOKENS_FOR_SAMPLING", "8000"))

    # Database Configuration
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:rasbem-8tucqi-qorsiD@db.defpdonvmsyycbjednxk.supabase.co:5432/postgres"
    )
    DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "20"))
    DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    DB_POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))
    DB_ECHO = os.getenv("DB_ECHO", "False").lower() == "true"

    # Supabase Configuration
    SUPABASE_URL = os.getenv("SUPABASE_URL", "https://defpdonvmsyycbjednxk.supabase.co")
    SUPABASE_API_KEY = os.getenv("Supabase_api_key", "")
    SUPABASE_SECRET_KEY = os.getenv("Supabase_secret_key", "")

    @classmethod
    def get_supabase_storage_url(cls) -> str:
        """Get Supabase storage URL with trailing slash"""
        base_url = cls.SUPABASE_URL.rstrip('/')
        return f"{base_url}/storage/v1/"

    # Supported file types
    SUPPORTED_EXCEL_EXTENSIONS = [".xlsx", ".xls"]
    SUPPORTED_CSV_EXTENSIONS = [".csv"]

    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        if not cls.OPENAI_API_KEY:
            return False
        if not cls.DATABASE_URL:
            return False
        return True
