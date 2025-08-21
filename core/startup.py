# core/startup.py
import warnings
import logging
import os
from colorama import init
from dotenv import load_dotenv

class ApplicationStartup:
    """Handles application initialization and environment setup"""
    
    @staticmethod
    def initialize_system():
        """Initialize system-level components"""
        # Suppress warnings
        ApplicationStartup._suppress_warnings()
        
        # Initialize colorama and load environment
        init(autoreset=True)
        load_dotenv()
        
        # Validate environment
        ApplicationStartup._validate_environment()
    
    @staticmethod
    def _suppress_warnings():
        """Suppress unnecessary warnings"""
        warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*was never awaited.*")
        warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*coroutine.*")
        warnings.filterwarnings("ignore", category=ResourceWarning, message=".*unclosed.*")
        warnings.filterwarnings("ignore", module="aiohttp")
        
        # Suppress logging noise
        logging.getLogger("asyncio").setLevel(logging.ERROR)
        logging.getLogger("aiohttp").setLevel(logging.ERROR)
    
    @staticmethod
    def _validate_environment():
        """Validate required environment variables"""
        required_vars = ["DISCORD_TOKEN"]
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")