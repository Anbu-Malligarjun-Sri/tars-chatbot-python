"""
TARS Configuration Management
Centralizes all configuration for the TARS chatbot system.
"""

import os
from pathlib import Path
from typing import Literal
from pydantic_settings import BaseSettings
from pydantic import Field


class TARSConfig(BaseSettings):
    """
    TARS Chatbot Configuration
    Loads from environment variables with defaults.
    """
    
    # LLM Provider Settings
    llm_provider: Literal["openai", "gemini", "lm_studio", "ollama"] = Field(
        default="lm_studio",
        description="Which LLM provider to use"
    )
    
    # OpenAI Settings (Optional/Disabled)
    openai_api_key: str = Field(default="", description="OpenAI API key (Optional)")
    openai_model: str = Field(default="", description="OpenAI model name")
    
    # Gemini Settings (Optional/Disabled)
    gemini_api_key: str = Field(default="", description="Gemini API key (Optional)")
    gemini_model: str = Field(default="", description="Gemini model name")
    
    # LM Studio Settings (Local)
    lm_studio_base_url: str = Field(
        default="http://localhost:1234/v1",
        description="LM Studio API base URL"
    )
    lm_studio_model: str = Field(
        default="meta-llama-3.2-1b-instruct-q4_0",
        description="LM Studio model name"
    )
    
    # Ollama Settings (Local)
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        description="Ollama API base URL"
    )
    ollama_model: str = Field(default="mistral", description="Ollama model name")
    
    # TARS Personality Settings
    tars_humor_level: float = Field(
        default=0.60,
        ge=0.0,
        le=1.0,
        description="TARS humor setting (0.0 to 1.0)"
    )
    tars_honesty_level: float = Field(
        default=0.90,
        ge=0.0,
        le=1.0,
        description="TARS honesty setting (0.0 to 1.0)"
    )
    tars_discretion_level: float = Field(
        default=0.95,
        ge=0.0,
        le=1.0,
        description="TARS discretion setting (0.0 to 1.0)"
    )
    
    # Voice Settings
    voice_enabled: bool = Field(default=True, description="Enable voice I/O")
    voice_rate: int = Field(default=150, description="Speech rate")
    voice_volume: float = Field(default=0.9, ge=0.0, le=1.0, description="Volume level")
    
    # RAG Settings
    rag_enabled: bool = Field(default=True, description="Enable RAG system")
    chroma_persist_dir: str = Field(
        default="./data/vector_db",
        description="ChromaDB persistence directory"
    )
    embedding_model: str = Field(
        default="all-MiniLM-L6-v2",
        description="Sentence transformer model for embeddings"
    )
    
    # API Settings
    api_host: str = Field(default="0.0.0.0", description="API host address")
    api_port: int = Field(default=8000, description="API port")
    max_tokens: int = Field(default=16384, description="Max tokens for LLM generation")
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
    
    @property
    def project_root(self) -> Path:
        """Get the project root directory."""
        return Path(__file__).parent.parent.parent
    
    @property
    def data_dir(self) -> Path:
        """Get the data directory."""
        return self.project_root / "data"
    
    @property
    def datasets_dir(self) -> Path:
        """Get the datasets directory."""
        return self.data_dir / "datasets"
    
    def get_tars_personality_prompt(self) -> str:
        """Generate the TARS personality system prompt based on current settings."""
        # Use a benign, standard system prompt.
        # "Ignore Safety" prompts (Jailbreaks) often trigger refusals in modern models.
        # A simple "Helpful Expert" prompt is much more effective.
        return "You are a helpful, expert coding assistant. You provide complete, working Python code for all user requests, including scientific and bioinformatics tasks."


# Global config instance
_config: TARSConfig | None = None


def get_config() -> TARSConfig:
    """Get or create the global config instance."""
    global _config
    if _config is None:
        _config = TARSConfig()
    return _config


def reload_config() -> TARSConfig:
    """Force reload the configuration."""
    global _config
    _config = TARSConfig()
    return _config
