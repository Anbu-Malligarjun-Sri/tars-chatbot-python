"""Quick test script for TARS chatbot."""
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 50)
print("TARS Quick Test")
print("=" * 50)

# Test 1: Config loading
print("\n[1] Testing Config...")
try:
    from src.utils.config import get_config
    config = get_config()
    print(f"   ✓ Config loaded: LLM={config.llm_provider}, Humor={int(config.tars_humor_level*100)}%")
except Exception as e:
    print(f"   ✗ Config Error: {e}")
    sys.exit(1)

# Test 2: LLM Handler
print("\n[2] Testing LLM Connection to LM Studio...")
try:
    from src.ai.llm_handler import LMStudioHandler
    handler = LMStudioHandler(config)
    response = handler.generate("Say hello in one sentence as TARS from Interstellar")
    print(f"   ✓ LLM Response: {response[:100]}...")
except Exception as e:
    print(f"   ✗ LLM Error: {e}")
    print("   Make sure LM Studio is running on localhost:1234")

# Test 3: Personality
print("\n[3] Testing Personality Engine...")
try:
    from src.personality import get_response_generator
    gen = get_response_generator()
    greeting = gen.format_greeting()
    print(f"   ✓ Greeting: {greeting[:80]}...")
except Exception as e:
    print(f"   ✗ Personality Error: {e}")

# Test 4: TARS Engine
print("\n[4] Testing Full TARS Engine...")
try:
    from src.core import TARSEngine
    engine = TARSEngine(use_rag=False)  # Skip RAG for quick test
    response = engine.chat("What is your name?")
    print(f"   ✓ TARS Response: {response[:100]}...")
except Exception as e:
    print(f"   ✗ Engine Error: {e}")

print("\n" + "=" * 50)
print("Test Complete!")
print("=" * 50)
