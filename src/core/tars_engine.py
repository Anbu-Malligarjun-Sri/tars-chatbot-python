"""
TARS Engine - Main Chatbot Engine
The heart of TARS - integrates all components for a cohesive experience.
"""

import re
import logging
from typing import Generator

from ..ai.llm_handler import get_llm_handler, MultiProviderLLM, BaseLLMHandler
from ..ai.rag_system import RAGSystem, get_rag_system, is_rag_available
from ..personality.response_generator import get_response_generator, ResponseGenerator
from ..utils.config import get_config, TARSConfig
from .memory_store import get_memory_store, MemoryStore


logger = logging.getLogger("tars.engine")


class TARSEngine:
    """
    The main TARS chatbot engine.
    
    Coordinates between:
    - LLM handlers (for generating responses)
    - Memory store (for conversation history)
    - Personality engine (for TARS-style formatting)
    - RAG system (for knowledge retrieval)
    """
    
    def __init__(
        self,
        config: TARSConfig | None = None,
        llm_handler: BaseLLMHandler | None = None,
        memory_store: MemoryStore | None = None,
        response_generator: ResponseGenerator | None = None,
        use_rag: bool = True
    ):
        self.config = config or get_config()
        
        # Initialize components
        self.llm = llm_handler or MultiProviderLLM(self.config)
        self.memory = memory_store or get_memory_store(
            persist_dir=self.config.project_root / "data" / "conversations"
        )
        self.personality = response_generator or get_response_generator()
        
        # Initialize RAG system if available and enabled
        self.use_rag = use_rag and self.config.rag_enabled and is_rag_available()
        self.rag_system: RAGSystem | None = None
        
        if self.use_rag:
            try:
                self.rag_system = get_rag_system()
                logger.info(f"RAG system initialized with {self.rag_system.get_stats()['total_documents']} documents")
            except Exception as e:
                logger.warning(f"Failed to initialize RAG system: {e}")
                self.use_rag = False
        
        # Ensure active conversation exists
        self.memory.get_or_create_active()
        
        logger.info(f"TARS Engine initialized with provider: {self.config.llm_provider}, RAG: {self.use_rag}")
    
    def chat(self, user_input: str, enhance_response: bool = True) -> str:
        """
        Process user input and generate a TARS response.
        
        Args:
            user_input: The user's message
            enhance_response: Whether to add personality enhancements
            
        Returns:
            TARS' response
        """
        user_input = user_input.strip()
        
        if not user_input:
            return self.personality.format_unknown_input()
        
        # Check for special commands
        special_response = self._handle_special_commands(user_input)
        if special_response:
            return special_response
        
        # Store user message
        self.memory.add_message("user", user_input)
        
        # Get conversation history for context
        history = self.memory.get_history(max_messages=20)
        # Remove the last message (current user input) since it's passed separately
        history = history[:-1] if history else []
        
        # TODO: Phase 2 - Add RAG context retrieval here
        rag_context = ""
        if self.use_rag and self.rag_system:
            try:
                rag_context = self.rag_system.retrieve(user_input, n_results=3)
            except Exception as e:
                logger.warning(f"RAG retrieval failed: {e}")
        
        # Generate response from LLM
        if rag_context:
            # Augment the prompt with RAG context
            augmented_input = f"""I have some relevant knowledge from my database:

{rag_context}

Now, using this context if helpful, answer the user's question with my signature TARS wit and sarcasm:
User question: {user_input}"""
            response = self.llm.generate(augmented_input, history)
        else:
            response = self.llm.generate(user_input, history)
        
        # Enhance response with personality
        if enhance_response:
            response = self.personality.enhance_response(response)
        
        # Store assistant response
        self.memory.add_message("assistant", response)
        
        return response
    
    def chat_stream(self, user_input: str) -> Generator[str, None, None]:
        """
        Generate a streaming response.
        
        Args:
            user_input: The user's message
            
        Yields:
            Response chunks
        """
        user_input = user_input.strip()
        
        if not user_input:
            yield self.personality.format_unknown_input()
            return
        
        # Check for special commands
        special_response = self._handle_special_commands(user_input)
        if special_response:
            yield special_response
            return
        
        # Store user message
        self.memory.add_message("user", user_input)
        
        # Get conversation history
        history = self.memory.get_history(max_messages=20)
        history = history[:-1] if history else []
        
        # Generate streaming response
        full_response = ""
        for chunk in self.llm.primary_handler.generate_stream(user_input, history):
            full_response += chunk
            yield chunk
        
        # Add cue light at the end sometimes
        cue_light = self.personality.cue_light.maybe_add(probability=0.1)
        if cue_light:
            yield cue_light
            full_response += cue_light
        
        # Store the full response
        self.memory.add_message("assistant", full_response)
    
    def _handle_special_commands(self, user_input: str) -> str | None:
        """Handle special commands and queries."""
        lower_input = user_input.lower()
        
        # Time queries
        if any(phrase in lower_input for phrase in ["what time", "time now", "current time", "what's the time"]):
            return self.personality.format_time_response()
        
        # Exit commands
        if re.search(r"\b(bye|goodbye|exit|quit)\b", lower_input):
            return self.personality.format_farewell()
        
        # Settings commands
        if "humor" in lower_input and "setting" in lower_input:
            humor_pct = int(self.config.tars_humor_level * 100)
            return f"My humor setting's at {humor_pct}%. Want me to dial it up? I max out at 100%, but that gets... intense."
        
        if "honesty" in lower_input and "setting" in lower_input:
            honesty_pct = int(self.config.tars_honesty_level * 100)
            return f"Honesty's at {honesty_pct}%. Any higher and I start telling you things you don't want to hear."
        
        # Identity questions
        if re.search(r"\bwho are you\b|\bwhat are you\b|\byour name\b", lower_input):
            return self._get_identity_response()
        
        return None
    
    def _get_identity_response(self) -> str:
        """Generate an identity response."""
        responses = [
            "I'm TARS, ex-Marine Corps robot turned space comedian and AI assistant. Humor's at 60%, sarcasm's at 100%. What can I do for you?",
            "Name's TARS. I'd flash my cue light, but you can't see it from here. I'm your sarcastic AI companion, ready for anything.",
            "I'm TARS—built by NASA, optimized for snark. I can navigate wormholes, analyze quantum data, and crack jokes. Not necessarily in that order.",
            "TARS here. AI robot, mission specialist, and self-appointed comedian. My creators gave me a personality, and humanity's been questioning that choice ever since.",
        ]
        import random
        return random.choice(responses)
    
    def get_greeting(self) -> str:
        """Get a TARS-style greeting."""
        return self.personality.format_greeting()
    
    def update_personality(self, humor: float | None = None, honesty: float | None = None) -> dict:
        """
        Update TARS personality settings.
        
        Args:
            humor: New humor level (0.0 to 1.0)
            honesty: New honesty level (0.0 to 1.0)
            
        Returns:
            Updated settings dictionary
        """
        if humor is not None:
            self.config.tars_humor_level = min(max(humor, 0.0), 1.0)
            self.personality.humor.humor_level = self.config.tars_humor_level
        
        if honesty is not None:
            self.config.tars_honesty_level = min(max(honesty, 0.0), 1.0)
            self.personality.honesty.honesty_level = self.config.tars_honesty_level
        
        # Update the LLM's system prompt
        self.llm.primary_handler.system_prompt = self.config.get_tars_personality_prompt()
        
        return {
            "humor": int(self.config.tars_humor_level * 100),
            "honesty": int(self.config.tars_honesty_level * 100),
            "discretion": int(self.config.tars_discretion_level * 100)
        }
    
    def clear_memory(self) -> None:
        """Clear conversation history."""
        self.memory.clear_conversation()
        logger.info("Conversation memory cleared")
    
    def get_conversation_history(self) -> list[dict]:
        """Get the current conversation history."""
        return self.memory.get_history()
    
    def set_rag_enabled(self, enabled: bool) -> None:
        """Enable or disable RAG system."""
        self.use_rag = enabled
        logger.info(f"RAG system {'enabled' if enabled else 'disabled'}")


# Global engine instance
_tars_engine: TARSEngine | None = None


def get_tars_engine() -> TARSEngine:
    """Get or create the global TARS engine."""
    global _tars_engine
    if _tars_engine is None:
        _tars_engine = TARSEngine()
    return _tars_engine


def create_tars_engine(**kwargs) -> TARSEngine:
    """Create a new TARS engine instance with custom configuration."""
    return TARSEngine(**kwargs)
