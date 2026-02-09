#!/usr/bin/env python3
"""
TARS Chatbot - Main Entry Point
Run this file to start TARS!

Usage:
    python main.py              # Start interactive chat
    python main.py --voice      # Start with voice mode
    python main.py --stream     # Start with streaming responses
    python main.py ask "question"  # Ask a single question
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.interfaces.cli import main


if __name__ == "__main__":
    main()
