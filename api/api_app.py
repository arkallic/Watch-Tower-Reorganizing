# api/api_app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import Request

# Import endpoint modules
from .endpoints import (
    health, bot_status, setup, users, cases, 
    statistics, moderators, analytics, settings, 
    spotlight, system
)

# Global dependencies - will be initialized from main.py
bot = None
config = None
logger = None
ollama = None
moderation_manager = None
deleted_message_logger = None
activity_tracker = None
bot_settings = None
modstring_manager = None

def initialize_api_dependencies(bot_instance, config_instance, logger_instance,
                              ollama_instance, moderation_manager_instance,
                              deleted_message_logger_instance, activity_tracker_instance,
                              bot_settings_instance, modstring_manager_instance):
    """Initialize API dependencies from main.py - accounts for reorganized structure"""
    global bot, config, logger, ollama, moderation_manager, deleted_message_logger
    global activity_tracker, bot_settings, modstring_manager
    
    bot = bot_instance
    config = config_instance
    logger = logger_instance
    ollama = ollama_instance
    moderation_manager = moderation_manager_instance
    deleted_message_logger = deleted_message_logger_instance
    activity_tracker = activity_tracker_instance
    bot_settings = bot_settings_instance
    modstring_manager = modstring_manager_instance
    
    # Initialize endpoint dependencies
    _initialize_endpoint_dependencies()

def _initialize_endpoint_dependencies():
    """Initialize dependencies for all endpoint modules"""
    try:
        # Health endpoint
        health.initialize_dependencies(
            bot, ollama, modstring_manager, activity_tracker, moderation_manager
        )
        
        # Bot status endpoint - UPDATED: Add missing dependencies
        bot_status.initialize_dependencies(bot, logger, ollama, modstring_manager)
        
        # Setup endpoint
        setup.initialize_dependencies(bot_settings)
        
        # Users endpoint - includes logger for risk calculation
        users.initialize_dependencies(
            bot, moderation_manager, deleted_message_logger, activity_tracker, logger
        )
        
        # Cases endpoint
        cases.initialize_dependencies(moderation_manager, bot)
        
        # Statistics endpoint - includes all loggers for comprehensive stats
        statistics.initialize_dependencies(
            moderation_manager, activity_tracker, bot, deleted_message_logger, logger
        )
        
        # Moderators endpoint
        moderators.initialize_dependencies(bot, moderation_manager, bot_settings)
        
        # Analytics endpoint - UPDATED: Add bot dependency for trends endpoint
        analytics.initialize_dependencies(moderation_manager, bot)
        
        # Settings endpoint
        settings.initialize_dependencies(bot_settings)
        
        # Spotlight endpoint
        spotlight.initialize_dependencies(bot, bot_settings)
        
        # System endpoint
        system.initialize_dependencies(bot)
        
        print("✅ All API endpoint dependencies initialized successfully")
        
    except Exception as e:
        print(f"❌ Error initializing endpoint dependencies: {e}")
        import traceback
        traceback.print_exc()

def create_api_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    app = FastAPI(
        title="Watch Tower Bot API",
        description="REST API for Watch Tower Discord moderation bot",
        version="2.0.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add cache control middleware
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
    
    # Include routers (each router should only be included once)
    app.include_router(health.router)
    app.include_router(bot_status.router)
    app.include_router(setup.router)
    app.include_router(users.router)
    app.include_router(cases.router)
    app.include_router(statistics.router)
    app.include_router(moderators.router)
    app.include_router(analytics.router)
    app.include_router(settings.router)
    app.include_router(spotlight.router)
    app.include_router(system.router)
    
    # Add error handlers
    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc):
        """Handle 404 errors properly"""
        return JSONResponse(
            status_code=404,
            content={"error": "Endpoint not found", "path": str(request.url)}
        )

    @app.exception_handler(500)
    async def server_error_handler(request: Request, exc):
        """Handle 500 errors properly"""
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "details": str(exc)}
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle all other exceptions"""
        return JSONResponse(
            status_code=500,
            content={"error": "An unexpected error occurred", "details": str(exc)}
        )
    
    return app

# Create the app instance
api_app = create_api_app()