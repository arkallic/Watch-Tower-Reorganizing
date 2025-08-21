# api/middleware/cors_cache.py
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware

def setup_middleware(app):
    """Setup CORS and cache middleware for the API"""
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add cache headers middleware
    @app.middleware("http")
    async def add_cache_headers(request: Request, call_next):
        response = await call_next(request)
        
        # Disable caching for all API responses
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        response.headers["Last-Modified"] = "0"
        response.headers["ETag"] = ""
        
        return response