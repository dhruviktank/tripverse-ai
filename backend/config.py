import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings and configuration."""
    
    # API Configuration
    api_title: str = "TripVerse AI Backend"
    api_description: str = "AI-powered trip planning API with LangGraph orchestration"
    api_version: str = "0.1.0"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # LLM Configuration
    gemini_api_key: str = ""
    grok_api_key: str = ""
    llm_provider: str = "gemini"  # "gemini" or "grok"
    llm_model: str = "gemini-1.5-flash"  # or "grok-3" for Grok
    llm_temperature: float = 0.7
    
    # Vector Database Configuration
    pinecone_api_key: str = ""
    pinecone_environment: str = "us-west-2-aws"
    pinecone_index_name: str = "tripverse-embeddings"
    
    # Vector Embedding Configuration
    embedding_model: str = "embedding-001"  # Google's embedding model
    embedding_dimension: int = 768

    # JIT RAG Search Configuration
    search_provider: str = "tavily"  # "tavily" or "serper"
    tavily_api_key: str = ""
    serper_api_key: str = ""
    search_results_count: int = 5
    max_article_chars: int = 4000
    
    # Database Configuration (Neon Postgres)
    database_url: str = ""

    # JWT Authentication Configuration
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiry_minutes: int = 1440  # 24 hours

    # Application Configuration
    max_retries: int = 5
    request_timeout: int = 120
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
