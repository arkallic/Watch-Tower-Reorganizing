# api/endpoints/__init__.py
"""
API endpoints package for Watch Tower Bot
All endpoint modules are imported here for easy access
"""

# Import all endpoint modules
from . import health
from . import bot_status
from . import setup
from . import users
from . import cases
from . import statistics
from . import moderators
from . import analytics
from . import settings
from . import spotlight
from . import system

__all__ = [
    'health',
    'bot_status', 
    'setup',
    'users',
    'cases',
    'statistics',
    'moderators',
    'analytics',
    'settings',
    'spotlight',
    'system'
]