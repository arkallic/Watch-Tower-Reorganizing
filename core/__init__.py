# core/__init__.py
"""
Core bot functionality and configuration
"""

from .config import ConfigManager
from .settings import BotSettings, bot_settings

__all__ = ['ConfigManager', 'BotSettings', 'bot_settings']