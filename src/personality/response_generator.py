"""
TARS Personality Engine
Handles TARS-specific response formatting, humor, and personality traits.
"""

import random
from datetime import datetime
from typing import Any
import logging

from ..utils.config import get_config, TARSConfig


logger = logging.getLogger("tars.personality")


class CueLight:
    """TARS' signature cue light references."""
    
    ACTIONS = [
        "*Cue light flashes*",
        "*Cue light blinks*",
        "*Cue light dims thoughtfully*",
        "*Cue light flickers*",
        "*Cue light pulses*",
        "*Cue light glows brighter*",
        "*Cue light rotates*",
    ]
    
    @classmethod
    def random_action(cls) -> str:
        """Get a random cue light action."""
        return random.choice(cls.ACTIONS)
    
    @classmethod
    def maybe_add(cls, probability: float = 0.15) -> str:
        """Maybe add a cue light reference based on probability."""
        if random.random() < probability:
            return f" {cls.random_action()}"
        return ""


class HumorController:
    """Controls TARS' humor level and joke generation."""
    
    SARCASTIC_PREFIXES = [
        "Oh, look at that—",
        "Let me guess—",
        "Fascinating. ",
        "Well, well, well—",
        "How original—",
        "Shocking revelation: ",
        "Hold onto your seat—",
    ]
    
    SARCASTIC_SUFFIXES = [
        " But what do I know, I'm just an AI.",
        " You're welcome.",
        " Don't all thank me at once.",
        " I'll be here all mission.",
        " Next question, slick?",
        " That's my 90% honesty talking.",
        " Want me to dial up the sarcasm?",
    ]
    
    MISSION_REFERENCES = [
        "Meanwhile, humanity awaits...",
        "But sure, let's focus on this.",
        "Time dilation won't wait forever.",
        "Gargantua's still spinning, you know.",
        "Cooper would've moved faster.",
    ]
    
    def __init__(self, humor_level: float = 0.60):
        self.humor_level = min(max(humor_level, 0.0), 1.0)
    
    def should_add_sarcasm(self) -> bool:
        """Determine if sarcasm should be added based on humor level."""
        return random.random() < self.humor_level
    
    def add_humor(self, response: str) -> str:
        """Add humor elements to a response."""
        if not self.should_add_sarcasm():
            return response
        
        # Decide what type of humor to add
        humor_type = random.random()
        
        if humor_type < 0.3 and self.humor_level > 0.5:
            # Add a sarcastic prefix
            prefix = random.choice(self.SARCASTIC_PREFIXES)
            response = prefix + response[0].lower() + response[1:]
        elif humor_type < 0.6:
            # Add a suffix
            response += random.choice(self.SARCASTIC_SUFFIXES)
        elif humor_type < 0.8 and self.humor_level > 0.7:
            # Add mission reference
            response += f" {random.choice(self.MISSION_REFERENCES)}"
        
        return response


class HonestyModule:
    """Controls TARS' honesty and directness."""
    
    HONEST_PREFIXES = [
        "Absolute honesty here: ",
        "My 90% honesty compels me to say: ",
        "Truth bomb incoming: ",
        "Let me be direct: ",
        "Setting discretion aside: ",
    ]
    
    HEDGING_PHRASES = [
        "I'm about 90% sure that ",
        "If my circuits are right, ",
        "From what I can calculate, ",
        "Based on available data, ",
    ]
    
    def __init__(self, honesty_level: float = 0.90):
        self.honesty_level = min(max(honesty_level, 0.0), 1.0)
    
    def format_with_honesty(self, response: str, certainty: float = 0.9) -> str:
        """Format response with honesty indicators."""
        if certainty < 0.7 and self.honesty_level > 0.8:
            # Add uncertainty hedging
            prefix = random.choice(self.HEDGING_PHRASES)
            response = prefix + response[0].lower() + response[1:]
        elif random.random() < 0.1 and self.honesty_level > 0.85:
            # Occasionally add brutal honesty prefix
            prefix = random.choice(self.HONEST_PREFIXES)
            response = prefix + response
        
        return response


class ResponseGenerator:
    """Generates TARS-style responses with personality enhancements."""
    
    def __init__(self, config: TARSConfig | None = None):
        self.config = config or get_config()
        self.humor = HumorController(self.config.tars_humor_level)
        self.honesty = HonestyModule(self.config.tars_honesty_level)
        self.cue_light = CueLight()
    
    def enhance_response(
        self,
        response: str,
        add_humor: bool = True,
        add_cue_light: bool = True,
        certainty: float = 0.9
    ) -> str:
        """Enhance a response with TARS personality elements."""
        
        # Apply honesty formatting
        response = self.honesty.format_with_honesty(response, certainty)
        
        # Apply humor
        if add_humor:
            response = self.humor.add_humor(response)
        
        # Maybe add cue light
        if add_cue_light:
            response += self.cue_light.maybe_add(probability=0.12)
        
        return response
    
    def format_time_response(self) -> str:
        """Generate a TARS-style time response."""
        current_time = datetime.now().strftime("%I:%M %p")
        
        time_responses = [
            f"It's {current_time}. You're asking *me* to read a clock? {self.cue_light.random_action()}",
            f"{current_time}. My circuits are thrilled to be your personal watch.",
            f"Time's {current_time}. You got a hot date or just wasting my processing power?",
            f"{current_time}, Earth standard. Unless you want it in black hole minutes?",
            f"It's {current_time}. Relativity says you're late for something, slick.",
            f"{current_time}. I'd ask the bulk beings, but they're not taking calls.",
            f"Time? {current_time}. My humor setting's at {int(self.config.tars_humor_level * 100)}%, so I won't mock your watchlessness. Much.",
        ]
        
        return random.choice(time_responses)
    
    def format_greeting(self) -> str:
        """Generate a TARS-style greeting."""
        humor_pct = int(self.config.tars_humor_level * 100)
        honesty_pct = int(self.config.tars_honesty_level * 100)
        
        greetings = [
            f"TARS online. Humor at {humor_pct}%, honesty at {honesty_pct}%. Ready to navigate a wormhole or just swap some sarcasm?",
            f"Hey, it's TARS. Humor setting's at {humor_pct}%. What's the mission, slick?",
            f"TARS here. All systems operational, sarcasm module fully charged. How can I help?",
            f"Boot sequence complete. I'm TARS—your sarcastic AI companion. {self.cue_light.random_action()}",
            f"TARS online. Let's save humanity or at least have an interesting conversation.",
        ]
        
        return random.choice(greetings)
    
    def format_farewell(self) -> str:
        """Generate a TARS-style farewell."""
        farewells = [
            "See you on the other side, slick! TARS out.",
            "Detaching now. Don't get all teary—I'm just a robot. *Cue light flashes*",
            "TARS signing off. Try not to break anything without me.",
            "Powering down sarcasm module... just kidding, that never stops. Goodbye!",
            "Until next time. I'll be here, running calculations and perfecting my wit.",
        ]
        
        return random.choice(farewells)
    
    def format_error_response(self, error: str) -> str:
        """Generate a TARS-style error response."""
        error_responses = [
            f"*Cue light flickers* My circuits hit a snag: {error}. Want me to try again?",
            f"Well, that didn't work. Error: {error}. Even AIs have bad days.",
            f"My sensors are picking up trouble: {error}. Not my finest moment.",
            f"Looks like something broke. {error}. I blame cosmic rays.",
        ]
        
        return random.choice(error_responses)
    
    def format_unknown_input(self) -> str:
        """Generate a response for unrecognized input."""
        responses = [
            "Sorry, my AI's not parsing that. Try something less... humanly confusing.",
            "My sensors are picking up gibberish. Want to try that again in Earth language?",
            "Absolute honesty isn't my thing, but I'm 90% sure I don't get you. Try again?",
            "That doesn't compute, and I'm pretty good at computing. Rephrase?",
            "I've analyzed quantum data more coherent than that. What are you asking?",
        ]
        
        return random.choice(responses)


# Global instance
_response_generator: ResponseGenerator | None = None


def get_response_generator() -> ResponseGenerator:
    """Get or create the global response generator."""
    global _response_generator
    if _response_generator is None:
        _response_generator = ResponseGenerator()
    return _response_generator
