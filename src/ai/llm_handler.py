"""
TARS LLM Handler
Unified interface for multiple LLM providers (OpenAI, Gemini, LM Studio, Ollama).
"""

from abc import ABC, abstractmethod
from typing import AsyncGenerator, Generator
import logging

from openai import OpenAI
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from ..utils.config import get_config, TARSConfig


logger = logging.getLogger("tars.llm")


class BaseLLMHandler(ABC):
    """Abstract base class for LLM handlers."""
    
    def __init__(self, config: TARSConfig):
        self.config = config
        self.system_prompt = config.get_tars_personality_prompt()
    
    @abstractmethod
    def generate(self, message: str, conversation_history: list[dict] | None = None) -> str:
        """Generate a response from the LLM."""
        pass
    
    @abstractmethod
    def generate_stream(self, message: str, conversation_history: list[dict] | None = None) -> Generator[str, None, None]:
        """Generate a streaming response from the LLM."""
        pass
    
    def _build_messages(self, message: str, conversation_history: list[dict] | None = None) -> list[dict]:
        """Build the messages list for the LLM."""
        messages = [{"role": "system", "content": self.system_prompt}]
        
        if conversation_history:
            messages.extend(conversation_history)
        
        messages.append({"role": "user", "content": message})
        return messages


class OpenAIHandler(BaseLLMHandler):
    """Handler for OpenAI API (including LM Studio compatibility)."""
    
    def __init__(self, config: TARSConfig, base_url: str | None = None, api_key: str | None = None, model: str | None = None):
        super().__init__(config)
        
        self.base_url = base_url or "https://api.openai.com/v1"
        self.api_key = api_key or config.openai_api_key
        self.model = model or config.openai_model
        
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        )
    
    def generate(self, message: str, conversation_history: list[dict] | None = None) -> str:
        """Generate a response using OpenAI-compatible API."""
        try:
            messages = self._build_messages(message, conversation_history)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=self.config.max_tokens
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return f"*Cue light flickers* My circuits hit a snag: {str(e)}. Want me to try again, or did you break something?"
    
    def generate_stream(self, message: str, conversation_history: list[dict] | None = None) -> Generator[str, None, None]:
        """Generate a streaming response."""
        try:
            messages = self._build_messages(message, conversation_history)
            
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=self.config.max_tokens,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        
        except Exception as e:
            logger.error(f"OpenAI streaming error: {e}")
            yield f"*Cue light dims* Stream disrupted: {str(e)}"


class LMStudioHandler(OpenAIHandler):
    """Handler for LM Studio (local LLM server)."""
    
    def __init__(self, config: TARSConfig):
        super().__init__(
            config,
            base_url=config.lm_studio_base_url,
            api_key="lm-studio",  # LM Studio doesn't need a real key
            model=config.lm_studio_model
        )


class OllamaHandler(BaseLLMHandler):
    """Handler for Ollama (local LLM)."""
    
    def __init__(self, config: TARSConfig):
        super().__init__(config)
        self.base_url = config.ollama_base_url
        self.model = config.ollama_model
        
        # Use OpenAI-compatible endpoint
        self.client = OpenAI(
            base_url=f"{self.base_url}/v1",
            api_key="ollama"  # Ollama doesn't need a real key
        )
    
    def generate(self, message: str, conversation_history: list[dict] | None = None) -> str:
        """Generate a response using Ollama."""
        try:
            messages = self._build_messages(message, conversation_history)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=self.config.max_tokens
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            return f"*Cue light flickers* Ollama's not responding. Is it running? Error: {str(e)}"
    
    def generate_stream(self, message: str, conversation_history: list[dict] | None = None) -> Generator[str, None, None]:
        """Generate a streaming response."""
        try:
            messages = self._build_messages(message, conversation_history)
            
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=self.config.max_tokens,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        
        except Exception as e:
            logger.error(f"Ollama streaming error: {e}")
            yield f"*Cue light dims* Stream error: {str(e)}"


class GeminiHandler(BaseLLMHandler):
    """Handler for Google Gemini API."""
    
    def __init__(self, config: TARSConfig):
        super().__init__(config)
        
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai package not installed")
        
        genai.configure(api_key=config.gemini_api_key)
        self.model = genai.GenerativeModel(
            model_name=config.gemini_model,
            system_instruction=self.system_prompt
        )
    
    def generate(self, message: str, conversation_history: list[dict] | None = None) -> str:
        """Generate a response using Gemini."""
        try:
            # Convert conversation history to Gemini format
            history = []
            if conversation_history:
                for msg in conversation_history:
                    role = "user" if msg["role"] == "user" else "model"
                    history.append({"role": role, "parts": [msg["content"]]})
            
            chat = self.model.start_chat(history=history)
            response = chat.send_message(message)
            
            return response.text.strip()
        
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            return f"*Cue light flickers* Gemini's being difficult: {str(e)}"
    
    def generate_stream(self, message: str, conversation_history: list[dict] | None = None) -> Generator[str, None, None]:
        """Generate a streaming response."""
        try:
            history = []
            if conversation_history:
                for msg in conversation_history:
                    role = "user" if msg["role"] == "user" else "model"
                    history.append({"role": role, "parts": [msg["content"]]})
            
            chat = self.model.start_chat(history=history)
            response = chat.send_message(message, stream=True)
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        
        except Exception as e:
            logger.error(f"Gemini streaming error: {e}")
            yield f"*Cue light dims* Stream error: {str(e)}"


def get_llm_handler(config: TARSConfig | None = None) -> BaseLLMHandler:
    """
    Factory function to get the appropriate LLM handler based on config.
    
    Args:
        config: Optional config override. Uses global config if not provided.
        
    Returns:
        Configured LLM handler instance
    """
    if config is None:
        config = get_config()
    
    provider = config.llm_provider.lower()
    
    if provider == "openai":
        return OpenAIHandler(config)
    elif provider == "gemini":
        return GeminiHandler(config)
    elif provider == "lm_studio":
        return LMStudioHandler(config)
    elif provider == "ollama":
        return OllamaHandler(config)
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")


class MultiProviderLLM:
    """
    Multi-provider LLM with automatic fallback.
    Tries the primary provider first, falls back to alternatives on failure.
    """
    
    def __init__(self, config: TARSConfig | None = None):
        self.config = config or get_config()
        self.primary_handler = get_llm_handler(self.config)
        self.fallback_handlers: list[BaseLLMHandler] = []
        
        # Set up fallbacks based on available providers
        self._setup_fallbacks()
    
    def _setup_fallbacks(self) -> None:
        """Set up fallback handlers."""
        providers_to_try = ["lm_studio", "ollama", "gemini", "openai"]
        primary = self.config.llm_provider.lower()
        
        for provider in providers_to_try:
            if provider != primary:
                try:
                    # Create a temporary config for the fallback provider
                    handler = self._create_handler_for_provider(provider)
                    if handler:
                        self.fallback_handlers.append(handler)
                except Exception:
                    pass  # Skip unavailable providers
    
    def _create_handler_for_provider(self, provider: str) -> BaseLLMHandler | None:
        """Create a handler for a specific provider."""
        if provider == "lm_studio":
            return LMStudioHandler(self.config)
        elif provider == "ollama":
            return OllamaHandler(self.config)
        elif provider == "gemini" and GEMINI_AVAILABLE and self.config.gemini_api_key:
            return GeminiHandler(self.config)
        elif provider == "openai" and self.config.openai_api_key:
            return OpenAIHandler(self.config)
        return None
    
    def generate(self, message: str, conversation_history: list[dict] | None = None) -> str:
        """Generate response with automatic fallback."""
        # Try primary handler
        try:
            return self.primary_handler.generate(message, conversation_history)
        except Exception as e:
            logger.warning(f"Primary LLM failed: {e}, trying fallbacks...")
        
        # Try fallback handlers
        for handler in self.fallback_handlers:
            try:
                return handler.generate(message, conversation_history)
            except Exception as e:
                logger.warning(f"Fallback LLM failed: {e}")
        
        # All handlers failed
        return "*Cue light goes dark* All my neural pathways are offline. Check your connections, slick."
