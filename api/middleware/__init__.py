# api/middleware/__init__.py
"""
FastAPI middleware components
"""

from .cors_cache import setup_middleware

__all__ = ['setup_middleware']