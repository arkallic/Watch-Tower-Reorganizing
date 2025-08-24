import discord
from discord.ext import commands
from typing import Dict, Any
from colorama import Fore, Style
import asyncio

################################################################################
# WATCH TOWER BOT CLASS
################################################################################

class WatchTowerBot(commands.Bot):
    """Main bot class with dependency injection"""
    
    # --------------------------------------------------------------------------
    # INITIALIZATION & DEPENDENCIES
    # --------------------------------------------------------------------------
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        intents.voice_states = True
        intents.reactions = True
        
        super().__init__(command_prefix='/', intents=intents)
        
        self.dependencies = {}
        self.ready_time = None
        self.service_check_task = None
        self.service_status = { "dashboard": False, "forge_studio": False }
    
    def inject_dependencies(self, dependencies: Dict[str, Any]):
        """Inject dependencies into the bot."""
        self.dependencies = dependencies
        print(f"{Fore.GREEN}✅ Dependencies injected into bot{Style.RESET_ALL}")
    
    def get_dependency(self, name: str):
        """Get a specific dependency."""
        return self.dependencies.get(name)

    # --------------------------------------------------------------------------
    # CORE BOT LIFECYCLE & EVENTS
    # --------------------------------------------------------------------------
    async def on_ready(self):
        """Called when bot is ready."""
        from datetime import datetime
        import platform
        self.ready_time = datetime.now()
        
        guild_count = len(self.guilds)
        total_members = sum(guild.member_count for guild in self.guilds)
        
        self._print_startup_banner(platform.python_version())
        await self._print_guild_info(guild_count, total_members)
        await self._initialize_integrations()
        self._print_available_services()
        await self._print_config_status()
        
        print(f"\n{Fore.GREEN}{Style.BRIGHT}🚀 WATCH TOWER IS READY FOR ACTION!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Monitoring {total_members:,} users across {guild_count} guild(s)...{Style.RESET_ALL}")
        
        self.service_check_task = asyncio.create_task(self.service_monitor_loop())
    
    async def on_message(self, message: discord.Message):
        """
        Handles incoming messages FOR COMMANDS ONLY.
        All other message processing (activity tracking, AI moderation) is now
        handled by the on_message event listener in main.py for better organization.
        """
        # We still need to ignore bots to prevent loops.
        if message.author.bot:
            return
        
        # This line is ESSENTIAL for your slash commands to be recognized and executed.
        # The discord.py library looks for this specific method to be called.
        await self.process_commands(message)

    async def close(self):
        """Clean up when bot is shutting down."""
        if self.service_check_task:
            self.service_check_task.cancel()
        await super().close()

    # --------------------------------------------------------------------------
    # BACKGROUND & HELPER METHODS
    # --------------------------------------------------------------------------
    async def service_monitor_loop(self):
        """Background task to monitor service availability."""
        while True:
            try:
                # Dashboard Check
                dashboard_up = await self.check_service_availability("http://localhost:3000")
                if dashboard_up != self.service_status["dashboard"]:
                    self.service_status["dashboard"] = dashboard_up
                    status = f"{Fore.GREEN}🟢 ONLINE{Style.RESET_ALL}" if dashboard_up else f"{Fore.RED}🔴 OFFLINE{Style.RESET_ALL}"
                    print(f"\nDashboard Status Update: {status}")

                # Forge Studio Check
                forge_up = await self.check_service_availability("http://localhost:8000")
                if forge_up != self.service_status["forge_studio"]:
                    self.service_status["forge_studio"] = forge_up
                    status = f"{Fore.GREEN}🟢 ONLINE{Style.RESET_ALL}" if forge_up else f"{Fore.RED}🔴 OFFLINE{Style.RESET_ALL}"
                    print(f"\nForge Studio Status Update: {status}")
                    if forge_up and (mod_manager := self.get_dependency('modstring_manager')):
                        await mod_manager.initialize()

                await asyncio.sleep(30)
            except Exception:
                await asyncio.sleep(30)
    
    # NOTE: The _process_ai_moderation method has been moved to the on_message listener in main.py
            
    async def check_service_availability(self, url: str, timeout: float = 2.0) -> bool:
        """Check if a service is available."""
        try:
            import aiohttp
            timeout_config = aiohttp.ClientTimeout(total=timeout)
            async with aiohttp.ClientSession(timeout=timeout_config) as session:
                async with session.get(url) as response:
                    return response.ok
        except:
            return False

    # --------------------------------------------------------------------------
    # STARTUP PRINTING METHODS
    # --------------------------------------------------------------------------
    def _print_startup_banner(self, python_version: str):
        """Prints the main startup banner and bot info."""
        print(f"\n{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║              🗼 {Fore.WHITE}{Style.BRIGHT}WATCH TOWER BOT ONLINE{Style.RESET_ALL}{Fore.CYAN}               ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}\n")
        print(f"{Fore.WHITE}{Style.BRIGHT}📊 BOT STATUS{Style.RESET_ALL}")
        print(f"   ├─ Bot User: {Fore.GREEN}{self.user.name}{Style.RESET_ALL}")
        print(f"   └─ Python: {Fore.MAGENTA}v{python_version}{Style.RESET_ALL}\n")

    async def _print_guild_info(self, guild_count: int, total_members: int):
        """Prints connected guild information."""
        print(f"{Fore.WHITE}{Style.BRIGHT}🏰 GUILD INFORMATION{Style.RESET_ALL}")
        if guild_count > 0:
            print(f"   └─ Connected to {Fore.CYAN}{guild_count}{Style.RESET_ALL} guild(s) with {Fore.YELLOW}{total_members:,}{Style.RESET_ALL} total members.")
        else:
            print(f"   └─ {Fore.RED}No guilds connected{Style.RESET_ALL}")
        print()

    async def _initialize_integrations(self):
        """Initializes and prints status for integrations like AI."""
        print(f"{Fore.WHITE}{Style.BRIGHT}🔧 INITIALIZING INTEGRATIONS{Style.RESET_ALL}")
        if ollama := self.get_dependency('ollama'):
            success = await ollama.initialize()
            print(f"   ├─ Ollama AI: {Fore.GREEN}Connected{Style.RESET_ALL}" if success else f"   ├─ Ollama AI: {Fore.RED}Connection Failed{Style.RESET_ALL}")
        else:
            print(f"   ├─ Ollama AI: {Fore.YELLOW}Not Configured{Style.RESET_ALL}")
        
        print(f"   └─ All integrations checked.")
        print()

    def _print_available_services(self):
        """Prints the available web service endpoints."""
        print(f"{Fore.WHITE}{Style.BRIGHT}🌐 AVAILABLE SERVICES{Style.RESET_ALL}")
        print(f"   ├─ Bot API: {Fore.GREEN}http://127.0.0.1:8001{Style.RESET_ALL}")
        print(f"   └─ Dashboard: {Fore.GREEN}http://localhost:3000{Style.RESET_ALL}")
        print()

    async def _print_config_status(self):
        """Prints a summary of the bot's current configuration."""
        from core.settings import bot_settings
        print(f"{Fore.WHITE}{Style.BRIGHT}⚙️  CONFIGURATION STATUS{Style.RESET_ALL}")
        config_items = [
            ("Bot Enabled", bot_settings.get("enabled", False)),
            ("AI Moderation", bot_settings.get("ai_enabled", False)),
        ]
        for name, is_enabled in config_items:
            status = f"{Fore.GREEN}✅ Enabled{Style.RESET_ALL}" if is_enabled else f"{Fore.RED}❌ Disabled{Style.RESET_ALL}"
            print(f"   ├─ {name}: {status}")
        
        watch_count = len(bot_settings.get("watch_channels", []))
        print(f"   └─ Watched Channels: {Fore.CYAN}{watch_count}{Style.RESET_ALL}")
        print()