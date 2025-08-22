# core/bot.py
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
        """Handle incoming messages."""
        if message.author.bot:
            return
        
        # Track all message activity
        if activity_tracker := self.get_dependency('activity_tracker'):
            await activity_tracker.track_message_activity(
                message.author.id, message.channel.id,
                message.guild.id if message.guild else 0,
                len(message.content), bool(message.attachments),
                bool(message.embeds), len(message.mentions)
            )
        
        # Process message for AI moderation
        await self._process_ai_moderation(message)
        
        # Process any application commands
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
    
    async def _process_ai_moderation(self, message: discord.Message):
        """Process message through AI moderation."""
        try:
            from core.settings import bot_settings
            if not bot_settings.get("ai_enabled", False): return
            
            watch_scope = bot_settings.get("watch_scope", "specific_channels")
            watch_channels = bot_settings.get("watch_channels", [])
            
            if watch_scope == "specific_channels" and message.channel.id not in watch_channels:
                return
            
            if (ollama := self.get_dependency('ollama')) and (logger := self.get_dependency('logger')):
                analysis = await ollama.analyze_message(message.content, message.author.id, message.channel.id)
                if analysis.get('should_flag', False):
                    await logger.log_flagged_message(
                        message.author.id, message.author.name, message.author.display_name,
                        message.content, message.created_at, message.jump_url,
                        confidence=analysis.get('confidence', 0), flags=analysis.get('flags', {}),
                        ai_explanation=analysis.get('reasoning', ''), channel_id=message.channel.id,
                        channel_name=message.channel.name
                    )
        except Exception as e:
            print(f"{Fore.RED}❌ AI moderation error: {e}{Style.RESET_ALL}")
            
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
        
        # ... You can add other integrations here ...
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