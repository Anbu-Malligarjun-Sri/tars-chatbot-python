"""TARS AI Package"""

from .llm_handler import (
    BaseLLMHandler,
    OpenAIHandler,
    GeminiHandler,
    LMStudioHandler,
    OllamaHandler,
    MultiProviderLLM,
    get_llm_handler
)
from .embeddings import EmbeddingGenerator, get_embedding_generator, EMBEDDINGS_AVAILABLE
from .vector_store import VectorStore, get_vector_store, CHROMA_AVAILABLE
from .rag_system import RAGSystem, get_rag_system, is_rag_available, DatasetLoader

__all__ = [
    "BaseLLMHandler",
    "OpenAIHandler", 
    "GeminiHandler",
    "LMStudioHandler",
    "OllamaHandler",
    "MultiProviderLLM",
    "get_llm_handler",
    "EmbeddingGenerator",
    "get_embedding_generator",
    "EMBEDDINGS_AVAILABLE",
    "VectorStore",
    "get_vector_store",
    "CHROMA_AVAILABLE",
    "RAGSystem",
    "get_rag_system",
    "is_rag_available",
    "DatasetLoader"
]
