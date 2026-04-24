"""Application configuration and settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings and configuration."""

    api_title: str = "TripVerse AI Backend"
    api_description: str = "AI-powered trip planning API with LangGraph orchestration"
    api_version: str = "0.1.0"

    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True

    gemini_api_key: str = ""
    grok_api_key: str = ""
    llm_provider: str = "gemini"
    llm_model: str = "gemini-1.5-flash"
    llm_temperature: float = 0.7

    pinecone_api_key: str = ""
    pinecone_environment: str = "us-west-2-aws"
    pinecone_index_name: str = "tripverse-embeddings"

    embedding_model: str = "embedding-001"
    embedding_dimension: int = 768

    search_provider: str = "tavily"
    tavily_api_key: str = ""
    serper_api_key: str = ""
    search_results_count: int = 5
    max_article_chars: int = 4000

    database_url: str = ""

    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiry_minutes: int = 1440

    max_retries: int = 5
    request_timeout: int = 120
    planning_debug_root: str = "debug_traces"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
