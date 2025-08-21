# api/api_app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .middleware.cors_cache import setup_middleware

# Import endpoint modules
from .endpoints import health, bot_status, setup, users, cases, statistics

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
    """Initialize API dependencies from main.py"""
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
        # Initialize each endpoint module with its required dependencies
        health.initialize_dependencies(
            bot, ollama, modstring_manager, activity_tracker, moderation_manager
        )
        
        bot_status.initialize_dependencies(bot, logger)
        
        setup.initialize_dependencies(bot_settings)
        
        users.initialize_dependencies(
            bot, moderation_manager, deleted_message_logger, activity_tracker
        )
        
        cases.initialize_dependencies(moderation_manager, bot)
        
        statistics.initialize_dependencies(moderation_manager, activity_tracker, bot)
        
    except Exception as e:
        print(f"Error initializing endpoint dependencies: {e}")

def create_api_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    app = FastAPI(
        title="Watch Tower Bot API",
        description="REST API for Watch Tower Discord moderation bot",
        version="2.0.0"
    )
    
    # Setup middleware
    setup_middleware(app)
    
    # Include routers
    app.include_router(health.router)
    app.include_router(bot_status.router)
    app.include_router(setup.router)
    app.include_router(users.router)
    app.include_router(cases.router)
    app.include_router(statistics.router)
    
    return app

# Create the app instance
api_app = create_api_app()