# main.py
"""
      ,   ,
     /////
    /////       Watch Tower
   |~~~|        ========================================================
   |[] |        An advanced, AI-powered moderation bot for Discord.
  /_____\       Features real-time ModString evaluation via Watch Tower Studio,
   |   |        a Dashboard, comprehensive logging, and powerful moderation tools.
   |   |
  /_____\
"""

import os
from colorama import Fore, Style

# ================================
# SYSTEM INITIALIZATION
# ================================
from core.startup import ApplicationStartup
from core.dependency_container import DependencyContainer
from core.bot import WatchTowerBot
from api.api_app import initialize_api_dependencies
from api.api_server import start_api_server

async def main():
    """Main application entry point"""
    print(f"{Fore.CYAN}🏗️  Starting Watch Tower Bot...{Style.RESET_ALL}")
    
    # Initialize system
    ApplicationStartup.initialize_system()
    print(f"{Fore.GREEN}✅ System initialized{Style.RESET_ALL}")
    
    # Initialize dependencies
    container = DependencyContainer()
    container.initialize_all_dependencies()
    print(f"{Fore.GREEN}✅ Dependencies initialized{Style.RESET_ALL}")
    
    # Debug: Print available dependencies
    deps = container.get_all_dependencies()
    print(f"{Fore.YELLOW}🔍 Available dependencies: {list(deps.keys())}{Style.RESET_ALL}")
    
    # Create and configure bot
    bot = WatchTowerBot()
    container.initialize_bot_dependent_components(bot)
    bot.inject_dependencies(deps)
    print(f"{Fore.GREEN}✅ Bot configured{Style.RESET_ALL}")
    
    # Initialize API dependencies
    try:
        # Check if bot_settings exists and fallback if needed
        bot_settings_instance = deps.get('bot_settings')
        if bot_settings_instance is None:
            print(f"{Fore.YELLOW}⚠️ bot_settings not found in dependencies, using config instead{Style.RESET_ALL}")
            # Try to get it from config
            config = deps.get('config')
            if config and hasattr(config, 'settings'):
                bot_settings_instance = config.settings
            else:
                # Import directly as fallback
                from core.settings import bot_settings
                bot_settings_instance = bot_settings
                print(f"{Fore.YELLOW}⚠️ Using direct import fallback for bot_settings{Style.RESET_ALL}")
        
        initialize_api_dependencies(
            bot, 
            deps['config'], 
            deps['logger'], 
            deps['ollama'],
            deps['moderation_manager'], 
            deps['deleted_message_logger'],
            deps['activity_tracker'], 
            bot_settings_instance,
            deps['modstring_manager']
        )
        print(f"{Fore.GREEN}✅ API dependencies initialized{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}❌ API initialization error: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()
    
    # Start API server
    if start_api_server():
        print(f"{Fore.GREEN}✅ API server started on http://127.0.0.1:8001{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}❌ Failed to start API server{Style.RESET_ALL}")
    
    # Start bot
    print(f"{Fore.BLUE}🤖 Starting Discord bot...{Style.RESET_ALL}")
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print(f"{Fore.RED}❌ DISCORD_TOKEN not found in environment variables{Style.RESET_ALL}")
        return
    
    try:
        await bot.start(token)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⏹️  Shutting down gracefully...{Style.RESET_ALL}")
        await bot.close()
    except Exception as e:
        print(f"{Fore.RED}❌ Bot startup error: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}👋 Watch Tower Bot stopped{Style.RESET_ALL}")