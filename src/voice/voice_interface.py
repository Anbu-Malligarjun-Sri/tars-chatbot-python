"""
TARS Voice Module
Handles speech recognition and text-to-speech functionality.
"""

import logging
from typing import Callable

try:
    import speech_recognition as sr
    import pyttsx3
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False
    sr = None
    pyttsx3 = None

from ..utils.config import get_config, TARSConfig


logger = logging.getLogger("tars.voice")


class VoiceInput:
    """Handles voice input using speech recognition."""
    
    def __init__(self, timeout: int = 5, phrase_time_limit: int = 10):
        if not VOICE_AVAILABLE:
            raise ImportError("speech_recognition package not installed")
        
        self.recognizer = sr.Recognizer()
        self.timeout = timeout
        self.phrase_time_limit = phrase_time_limit
        
        # Adjust for ambient noise on first use
        self._calibrated = False
    
    def calibrate(self) -> None:
        """Calibrate the recognizer for ambient noise."""
        try:
            with sr.Microphone() as source:
                logger.info("Calibrating for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                self._calibrated = True
                logger.info("Calibration complete")
        except Exception as e:
            logger.error(f"Calibration failed: {e}")
    
    def listen(self, prompt_callback: Callable[[str], None] | None = None) -> str | None:
        """
        Listen for voice input.
        
        Args:
            prompt_callback: Optional callback to show listening prompt
            
        Returns:
            Transcribed text or None on failure
        """
        if not VOICE_AVAILABLE:
            return None
        
        if not self._calibrated:
            self.calibrate()
        
        try:
            with sr.Microphone() as source:
                if prompt_callback:
                    prompt_callback("Listening... Want me to turn on my cue light?")
                else:
                    logger.info("Listening...")
                
                audio = self.recognizer.listen(
                    source,
                    timeout=self.timeout,
                    phrase_time_limit=self.phrase_time_limit
                )
                
                # Transcribe using Google Speech Recognition
                text = self.recognizer.recognize_google(audio)
                logger.info(f"Heard: {text}")
                return text
        
        except sr.UnknownValueError:
            logger.warning("Could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(f"Speech recognition request failed: {e}")
            return None
        except sr.WaitTimeoutError:
            logger.warning("No speech detected")
            return None
        except Exception as e:
            logger.error(f"Voice input error: {e}")
            return None
    
    def get_error_message(self, error_type: str) -> str:
        """Get a TARS-style error message for voice issues."""
        messages = {
            "not_understood": "Sorry, my audio sensors couldn't parse that. Try again?",
            "request_error": "Comm error. My circuits aren't liking this planet's atmosphere.",
            "timeout": "No input detected. You trying to test my patience setting?",
            "general": "Voice systems experiencing turbulence. Want to type instead?",
        }
        return messages.get(error_type, messages["general"])


class VoiceOutput:
    """Handles text-to-speech output."""
    
    def __init__(self, config: TARSConfig | None = None):
        if not VOICE_AVAILABLE:
            raise ImportError("pyttsx3 package not installed")
        
        self.config = config or get_config()
        self.engine = pyttsx3.init()
        
        # Configure voice properties
        self._configure_voice()
    
    def _configure_voice(self) -> None:
        """Configure the TTS engine with TARS-like settings."""
        self.engine.setProperty('rate', self.config.voice_rate)
        self.engine.setProperty('volume', self.config.voice_volume)
        
        # Try to find a suitable voice (prefer male voices for TARS)
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if 'male' in voice.name.lower() or 'david' in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                logger.info(f"Using voice: {voice.name}")
                break
    
    def speak(self, text: str, block: bool = True) -> None:
        """
        Speak text aloud.
        
        Args:
            text: Text to speak
            block: Whether to block until speech is complete
        """
        if not VOICE_AVAILABLE:
            return
        
        # Clean text for speech (remove asterisks for cue light actions)
        clean_text = text.replace('*', '').replace('_', '')
        
        logger.debug(f"Speaking: {clean_text[:50]}...")
        self.engine.say(clean_text)
        
        if block:
            self.engine.runAndWait()
    
    def speak_async(self, text: str) -> None:
        """Speak text without blocking."""
        self.speak(text, block=False)
    
    def stop(self) -> None:
        """Stop current speech."""
        if VOICE_AVAILABLE:
            self.engine.stop()
    
    def set_rate(self, rate: int) -> None:
        """Set speech rate (words per minute)."""
        self.engine.setProperty('rate', rate)
    
    def set_volume(self, volume: float) -> None:
        """Set volume (0.0 to 1.0)."""
        self.engine.setProperty('volume', min(max(volume, 0.0), 1.0))


class VoiceInterface:
    """Combined voice input/output interface for TARS."""
    
    def __init__(self, config: TARSConfig | None = None):
        self.config = config or get_config()
        self.enabled = self.config.voice_enabled and VOICE_AVAILABLE
        
        self.input: VoiceInput | None = None
        self.output: VoiceOutput | None = None
        
        if self.enabled:
            try:
                self.input = VoiceInput()
                self.output = VoiceOutput(self.config)
                logger.info("Voice interface initialized")
            except Exception as e:
                logger.error(f"Failed to initialize voice: {e}")
                self.enabled = False
    
    def listen_and_respond(
        self,
        response_generator: Callable[[str], str],
        greeting: str | None = None
    ) -> None:
        """
        Start a voice conversation loop.
        
        Args:
            response_generator: Function that takes user input and returns response
            greeting: Optional greeting to speak first
        """
        if not self.enabled:
            logger.error("Voice interface not available")
            return
        
        if greeting:
            self.speak(greeting)
        
        while True:
            # Listen for input
            user_input = self.listen()
            
            if user_input is None:
                self.speak(self.input.get_error_message("not_understood"))
                continue
            
            # Check for exit
            if any(word in user_input.lower() for word in ['bye', 'goodbye', 'exit', 'quit']):
                break
            
            # Generate and speak response
            response = response_generator(user_input)
            self.speak(response)
    
    def listen(self, prompt: str | None = None) -> str | None:
        """Listen for voice input."""
        if self.input is None:
            return None
        
        callback = (lambda msg: print(msg)) if prompt else None
        return self.input.listen(callback)
    
    def speak(self, text: str) -> None:
        """Speak text aloud."""
        if self.output:
            self.output.speak(text)
    
    def is_available(self) -> bool:
        """Check if voice is available."""
        return self.enabled


# Convenience function
def create_voice_interface() -> VoiceInterface | None:
    """Create a voice interface if available."""
    try:
        vi = VoiceInterface()
        return vi if vi.enabled else None
    except Exception:
        return None
