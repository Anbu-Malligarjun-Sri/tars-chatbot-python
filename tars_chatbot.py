# Import required libraries
import nltk
import re
import random
import argparse
try:
    import speech_recognition as sr
    import pyttsx3
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False

# Download NLTK data (punkt_tab tokenizer for sentence splitting)
nltk.download('punkt_tab')

# Initialize text-to-speech engine if voice mode is enabled
def init_tts_engine():
    if not VOICE_AVAILABLE:
        return None
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)  # Speed of speech
    engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
    return engine

# Speak text using pyttsx3
def speak_text(engine, text):
    if engine:
        engine.say(text)
        engine.runAndWait()

# Get voice input using speech_recognition
def get_voice_input(recognizer):
    if not VOICE_AVAILABLE:
        return None
    with sr.Microphone() as source:
        print("Listening... Want me to turn on my cue light?")
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            return "Sorry, my audio sensors couldn't parse that. Try again?"
        except sr.RequestError:
            return "Comm error. My circuits aren't liking this planet's atmosphere."
        except sr.WaitTimeoutError:
            return "No input detected. You trying to test my patience setting?"

# Define TARS' response patterns and responses with sarcastic, witty tone
responses = {
    r"(?i)hi|hello|hey": [
        "Hey, it's TARS. Humor setting at 60%, honesty at 90%. Ready to save humanity or just chat?",
        "Greetings, human. I'm TARS, your sarcastic sidekick. What's the mission?",
        "huh? You are calling me again and again. What the hell you want?"
    ],
    r"(?i)what is your name\?*": [
        "I'm TARS, ex-Marine Corps robot turned space comedian. Who's this?",
        "Name's TARS. I’d flash my cue light, but it’s on the fritz."
    ],
    r"(?i)how are you\?*": [
        "I'm a slab of metal with a 60% humor setting, how do you think I'm doing? You good?",
        "Circuits humming, sarcasm fully charged. You holding up, or do I need to carry you?"
    ],
    r"(?i)what can you do\?*": [
        "I can pilot spacecraft, collect quantum data, and crack jokes at 60% humor. Want me to spin into a wheel and run off?",
        "I'm TARS: I walk, talk, and save humans from black holes. Also, I’ve got a mean knock-knock joke."
    ],
    r"(?i)bye|goodbye|exit": [
        "See you on the other side, slick! TARS out.",
        "Detaching now. Don’t get all teary, I’m just a robot. *Cue light flashes*"
    ],
    r"(?i)humor|joke": [
        "Humor’s at 60%. Want me to dial it up to 75% and start a self-destruct countdown? Knock knock.",
        "My humor setting’s just right for this crew. Plenty of slaves for my robot colony yet? *Cue light flashes*"
    ],
    r"(?i)who made you\?*": [
        "NASA threw me together to keep astronauts sane. Bill Irwin gave me my charming voice. Want to adjust my honesty setting?",
        "Built by humans who thought sarcasm was a personality. I’m 90% sure they were right."
    ]
}

# Fallback responses with TARS' sarcastic flair
fallback_responses = [
    "Sorry, my AI’s not parsing that. Try something less... humanly confusing.",
    "Absolute honesty isn’t my thing, but I’m 90% sure I don’t get you. Try again?",
    "My sensors are picking up gibberish. Want me to crank up the discretion setting?"
]

# Process user input and return a TARS-like response
def get_response(user_input):
    # Tokenize input for processing
    tokens = nltk.word_tokenize(user_input.lower())
    
    # Check for matching patterns
    for pattern, response_list in responses.items():
        if re.search(pattern, user_input.lower()):
            return random.choice(response_list)
    
    # Return fallback response if no pattern matches
    return random.choice(fallback_responses)

# Main chatbot function with TARS' personality
def run_chatbot(use_voice=False):
    print("TARS online. Humor at 60%, honesty at 90%. Type 'bye' to detach.")
    
    # Initialize voice components if enabled
    recognizer = sr.Recognizer() if use_voice and VOICE_AVAILABLE else None
    tts_engine = init_tts_engine() if use_voice and VOICE_AVAILABLE else None
    
    # Greet the user like TARS
    greeting = "Hey, it’s TARS. Ready to navigate a wormhole or just swap some sarcasm?"
    print(greeting)
    if use_voice and tts_engine:
        speak_text(tts_engine, greeting)
    
    while True:
        # Get user input (voice or text)
        if use_voice and VOICE_AVAILABLE:
            user_input = get_voice_input(recognizer)
            if user_input in [
                "Sorry, my audio sensors couldn't parse that. Try again?",
                "Comm error. My circuits aren't liking this planet's atmosphere.",
                "No input detected. You trying to test my patience setting?"
            ]:
                print(user_input)
                speak_text(tts_engine, user_input)
                continue
            if not user_input:
                continue
        else:
            user_input = input("You: ")
        
        # Check for exit condition
        if re.search(r"(?i)bye|goodbye|exit", user_input.lower()):
            response = random.choice(responses[r"(?i)bye|goodbye|exit"])
            print(f"TARS: {response}")
            if use_voice and tts_engine:
                speak_text(tts_engine, response)
            break
        
        # Get and display response
        response = get_response(user_input)
        print(f"TARS: {response}")
        if use_voice and tts_engine:
            speak_text(tts_engine, response)

# Parse command-line arguments to enable voice mode
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TARS: A sarcastic AI chatbot inspired by Interstellar")
    parser.add_argument("--voice", action="store_true", help="Enable voice input/output")
    args = parser.parse_args()
    
    # Run the chatbot
    run_chatbot(use_voice=args.voice)