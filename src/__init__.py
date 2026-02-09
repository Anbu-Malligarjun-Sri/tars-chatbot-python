"""TARS Chatbot - Main Package"""

from .core import TARSEngine, get_tars_engine, create_tars_engine
from .utils import get_config, TARSConfig
from .personality import get_response_generator

__version__ = "2.0.0"

__all__ = [
    "TARSEngine",
    "get_tars_engine",
    "create_tars_engine",
    "get_config",
    "TARSConfig",
    "get_response_generator",
    "__version__"
]
