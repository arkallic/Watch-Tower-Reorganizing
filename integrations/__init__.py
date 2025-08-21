# integrations/__init__.py
"""
External service integrations
"""

from .ollama_client import OllamaClient
from .modstring_manager import ModStringManager

__all__ = ['OllamaClient', 'ModStringManager']