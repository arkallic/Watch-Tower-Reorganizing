# core/bot.py
import discord
from discord.ext import commands
from typing import Dict, Any
from colorama import Fore, Style

class WatchTowerBot(commands.Bot):
    """Main bot class with dependency injection"""
    
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
        self.service_status = {
            "dashboard": False,
            "forge_studio": False
        }
    
    def inject_dependencies(self, dependencies: Dict[str, Any]):
        """Inject dependencies into the bot"""
        self.dependencies = dependencies
        print(f"{Fore.GREEN}✅ Dependencies injected into bot{Style.RESET_ALL}")
    
    def get_dependency(self, name: str):
        """Get a specific dependency"""
        return self.dependencies.get(name)
    
    async def check_service_availability(self, url: str, timeout: float = 2.0) -> bool:
        """Check if a service is available"""
        try:
            import aiohttp
            timeout_config = aiohttp.ClientTimeout(total=timeout, connect=timeout)
            async with aiohttp.ClientSession(timeout=timeout_config) as session:
                async with session.get(url) as response:
                    return response.status == 200
        except:
            return False
    
    async def service_monitor_loop(self):
        """Background task to monitor service availability"""
        import asyncio
        
        while True:
            try:
                # Check dashboard
                dashboard_available = await self.check_service_availability("http://localhost:3000")
                if dashboard_available and not self.service_status["dashboard"]:
                    self.service_status["dashboard"] = True
                    print(f"\n{Fore.GREEN}🟢 Dashboard came online: {Fore.WHITE}http://localhost:3000{Style.RESET_ALL}")
                elif not dashboard_available and self.service_status["dashboard"]:
                    self.service_status["dashboard"] = False
                    print(f"\n{Fore.RED}🔴 Dashboard went offline{Style.RESET_ALL}")
                
                # Check Forge Studio
                forge_available = await self.check_service_availability("http://localhost:8000")
                modstring_manager = self.get_dependency('modstring_manager')
                
                if forge_available and not self.service_status["forge_studio"]:
                    self.service_status["forge_studio"] = True
                    print(f"\n{Fore.GREEN}🟢 Forge Studio came online: {Fore.WHITE}http://localhost:8000{Style.RESET_ALL}")
                    
                    # Re-initialize ModString manager
                    if modstring_manager:
                        print(f"{Fore.YELLOW}🔄 Re-syncing ModStrings...{Style.RESET_ALL}")
                        await modstring_manager.initialize()
                        if modstring_manager.enabled:
                            print(f"{Fore.GREEN}✅ ModString sync completed ({len(modstring_manager.active_modstrings)} ModStrings loaded){Style.RESET_ALL}")
                
                elif not forge_available and self.service_status["forge_studio"]:
                    self.service_status["forge_studio"] = False
                    print(f"\n{Fore.RED}🔴 Forge Studio went offline{Style.RESET_ALL}")
                    if modstring_manager:
                        modstring_manager.enabled = False
                
                # Wait 30 seconds before next check
                await asyncio.sleep(30)
                
            except Exception as e:
                # If there's an error, wait and continue
                await asyncio.sleep(30)
    
    async def on_ready(self):
        """Called when bot is ready"""
        from datetime import datetime
        import platform
        import asyncio
        self.ready_time = datetime.now()
        
        # Get system info
        guild_count = len(self.guilds)
        total_members = sum(guild.member_count for guild in self.guilds)
        python_version = platform.python_version()
        
        # Startup animation without clearing screen
        print()
        frames = [
            "🏗️  Initializing Watch Tower...",
            "🔧 Loading systems...", 
            "⚡ Powering up...",
            "🛡️  Activating defenses...",
            "🗼 Watch Tower Online!"
        ]
        
        for frame in frames:
            print(f"{Fore.CYAN}{frame}{Style.RESET_ALL}")
            await asyncio.sleep(0.5)
        
        print()
        
        # Show banner
        print(f"{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║                                                              ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║              🗼 {Fore.WHITE}{Style.BRIGHT}WATCH TOWER BOT ONLINE{Style.RESET_ALL}{Fore.CYAN}               ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║                                                              ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
        print()
        
        # Bot Information
        print(f"{Fore.WHITE}{Style.BRIGHT}📊 BOT STATUS{Style.RESET_ALL}")
        print(f"   ├─ Bot User: {Fore.GREEN}{self.user.name}#{self.user.discriminator}{Style.RESET_ALL}")
        print(f"   ├─ Bot ID: {Fore.YELLOW}{self.user.id}{Style.RESET_ALL}")
        print(f"   ├─ Ready Time: {Fore.CYAN}{self.ready_time.strftime('%H:%M:%S')}{Style.RESET_ALL}")
        print(f"   └─ Python: {Fore.MAGENTA}v{python_version}{Style.RESET_ALL}")
        print()
        
        # Guild Information with animation
        print(f"{Fore.WHITE}{Style.BRIGHT}🏰 GUILD INFORMATION{Style.RESET_ALL}")
        if guild_count > 0:
            for i, guild in enumerate(self.guilds, 1):
                print(f"   ├─ {Fore.GREEN}{guild.name}{Style.RESET_ALL} ({Fore.YELLOW}{guild.member_count:,} members{Style.RESET_ALL})")
                await asyncio.sleep(0.2)
                print(f"   │  ├─ Channels: {len(guild.channels)}")
                print(f"   │  ├─ Roles: {len(guild.roles)}")
                print(f"   │  └─ Owner: {guild.owner.display_name if guild.owner else 'Unknown'}")
            print(f"   └─ Total: {Fore.CYAN}{guild_count} guild(s), {total_members:,} members{Style.RESET_ALL}")
        else:
            print(f"   └─ {Fore.RED}No guilds connected{Style.RESET_ALL}")
        print()
        
        # Initialize and show integration status with animations
        print(f"{Fore.WHITE}{Style.BRIGHT}🔧 INITIALIZING INTEGRATIONS{Style.RESET_ALL}")
        
        # Initialize Ollama with animation
        ollama = self.get_dependency('ollama')
        if ollama:
            print(f"   ├─ {Fore.YELLOW}Connecting to Ollama AI...{Style.RESET_ALL}")
            await asyncio.sleep(0.3)
            success = await ollama.initialize()
            if success:
                print(f"   ├─ {Fore.GREEN}✅ Ollama AI: Connected and ready{Style.RESET_ALL}")
            else:
                print(f"   ├─ {Fore.RED}❌ Ollama AI: Connection failed{Style.RESET_ALL}")
        else:
            print(f"   ├─ {Fore.RED}❌ Ollama AI: Not configured{Style.RESET_ALL}")
        
        await asyncio.sleep(0.2)
        
        # Initialize ModString Manager with animation
        modstring_manager = self.get_dependency('modstring_manager')
        if modstring_manager:
            print(f"   ├─ {Fore.YELLOW}Connecting to Forge Studio...{Style.RESET_ALL}")
            await asyncio.sleep(0.3)
            await modstring_manager.initialize()
            if modstring_manager.enabled:
                print(f"   ├─ {Fore.GREEN}✅ Forge Studio: Connected ({len(modstring_manager.active_modstrings)} ModStrings loaded){Style.RESET_ALL}")
                self.service_status["forge_studio"] = True
            else:
                print(f"   ├─ {Fore.YELLOW}⚠️  Forge Studio: Offline (Monitoring for connection...){Style.RESET_ALL}")
                self.service_status["forge_studio"] = False
        else:
            print(f"   ├─ {Fore.RED}❌ Forge Studio: Not configured{Style.RESET_ALL}")
        
        await asyncio.sleep(0.2)
        
        # Show other service statuses with small delays
        services = [
            ("Activity Tracker", "✅", "Active"),
            ("Message Logger", "✅", "Active"), 
            ("Moderation System", "✅", "Active"),
            ("API Server", "✅", "http://127.0.0.1:8001")
        ]
        
        for i, (service, status, info) in enumerate(services):
            if i < len(services) - 1:
                print(f"   ├─ {Fore.GREEN}{status} {service}: {info}{Style.RESET_ALL}")
            else:
                print(f"   └─ {Fore.GREEN}{status} {service}: {info}{Style.RESET_ALL}")
            await asyncio.sleep(0.1)
        
        print()
        
        # Show available endpoints
        print(f"{Fore.WHITE}{Style.BRIGHT}🌐 AVAILABLE SERVICES{Style.RESET_ALL}")
        
        # Check Dashboard
        print(f"   ├─ {Fore.YELLOW}Checking Dashboard...{Style.RESET_ALL}")
        await asyncio.sleep(0.3)
        dashboard_available = await self.check_service_availability("http://localhost:3000")
        if dashboard_available:
            print(f"   ├─ {Fore.GREEN}✅ Dashboard: http://localhost:3000{Style.RESET_ALL}")
            self.service_status["dashboard"] = True
        else:
            print(f"   ├─ {Fore.RED}❌ Dashboard: http://localhost:3000 (Monitoring for connection...){Style.RESET_ALL}")
            self.service_status["dashboard"] = False
        
        await asyncio.sleep(0.2)
        
        # Bot API (should be online since we started it)
        print(f"   ├─ {Fore.GREEN}✅ Bot API: http://localhost:8001{Style.RESET_ALL}")
        
        # Health Check (should be online)
        print(f"   ├─ {Fore.GREEN}✅ Health Check: http://localhost:8001/health{Style.RESET_ALL}")
        
        # Forge Studio (use existing status)
        if self.service_status["forge_studio"]:
            print(f"   └─ {Fore.GREEN}✅ Forge Studio: http://localhost:8000{Style.RESET_ALL}")
        else:
            print(f"   └─ {Fore.YELLOW}⚠️  Forge Studio: http://localhost:8000 (Monitoring for connection...){Style.RESET_ALL}")

        print()
        
        # Show configuration status
        from core.settings import bot_settings
        enabled = bot_settings.get("enabled", False)
        ai_enabled = bot_settings.get("ai_enabled", False)
        watch_channels = len(bot_settings.get("watch_channels", []))
        
        print(f"{Fore.WHITE}{Style.BRIGHT}⚙️  CONFIGURATION STATUS{Style.RESET_ALL}")
        config_items = [
            ("Bot Enabled", enabled, "✅ Yes" if enabled else "❌ No"),
            ("AI Moderation", ai_enabled, "✅ Enabled" if ai_enabled else "⚠️  Disabled"),
            ("Watched Channels", True, f"{watch_channels}"),
            ("Debug Mode", True, f"{'✅ On' if bot_settings.get('debug_mode') else '⚠️  Off'}")
        ]
        
        for i, (setting, status, value) in enumerate(config_items):
            color = Fore.GREEN if status else (Fore.YELLOW if "⚠️" in value else Fore.RED)
            if i < len(config_items) - 1:
                print(f"   ├─ {setting}: {color}{value}{Style.RESET_ALL}")
            else:
                print(f"   └─ {setting}: {color}{value}{Style.RESET_ALL}")
            await asyncio.sleep(0.1)
        
        print()
        
        # Final status with animation
        final_messages = [
            f"{Fore.GREEN}{Style.BRIGHT}🚀 WATCH TOWER IS READY FOR ACTION!{Style.RESET_ALL}",
            f"{Fore.WHITE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Style.RESET_ALL}",
            f"{Fore.CYAN}Monitoring {total_members:,} users across {guild_count} guild(s)...{Style.RESET_ALL}",
            f"{Fore.YELLOW}Automatically checking for Dashboard and Forge Studio every 30 seconds{Style.RESET_ALL}",
            f"{Fore.YELLOW}Press Ctrl+C to stop the bot{Style.RESET_ALL}"
        ]
        
        for message in final_messages:
            print(message)
            await asyncio.sleep(0.3)
        
        print()
        
        # Start the service monitoring task
        self.service_check_task = asyncio.create_task(self.service_monitor_loop())
    
    async def close(self):
        """Clean up when bot is shutting down"""
        if self.service_check_task:
            self.service_check_task.cancel()
        await super().close()
    
    async def on_message(self, message):
        """Handle incoming messages"""
        if message.author.bot:
            return
        
        # Activity tracking
        activity_tracker = self.get_dependency('activity_tracker')
        if activity_tracker:
            await activity_tracker.track_message_activity(
                message.author.id,
                message.channel.id,
                message.guild.id if message.guild else 0,
                len(message.content),
                bool(message.attachments),
                bool(message.embeds),
                len(message.mentions)
            )
        
        # AI moderation (if enabled)
        await self._process_ai_moderation(message)
        
        # Process commands
        await self.process_commands(message)
    
    async def on_message_delete(self, message):
        """Handle message deletion"""
        if message.author.bot:
            return
        
        deleted_message_logger = self.get_dependency('deleted_message_logger')
        if deleted_message_logger:
            await deleted_message_logger.log_deleted_message(message)
    
    async def _process_ai_moderation(self, message):
        """Process message through AI moderation"""
        try:
            from core.settings import bot_settings
            
            if not bot_settings.get("ai_enabled", False):
                return
            
            # Check if channel is being watched
            watch_scope = bot_settings.get("watch_scope", "specific_channels")
            watch_channels = bot_settings.get("watch_channels", [])
            
            if watch_scope == "specific_channels" and message.channel.id not in watch_channels:
                return
            
            # Get AI client
            ollama = self.get_dependency('ollama')
            if not ollama:
                return
            
            # Analyze message
            analysis = await ollama.analyze_message(
                message.content,
                message.author.id,
                message.channel.id
            )
            
            # Check if should flag
            logger = self.get_dependency('logger')
            if logger and analysis.get('should_flag', False):
                await logger.log_flagged_message(
                    message.author.id,
                    message.author.name,
                    message.author.display_name,
                    message.content,
                    message.created_at,
                    message.jump_url,
                    analysis.get('confidence', 0),
                    analysis.get('flags', {}),
                    analysis.get('reasoning', ''),
                    message.channel.id,
                    message.channel.name
                )
        
        except Exception as e:
            print(f"{Fore.RED}❌ AI moderation error: {e}{Style.RESET_ALL}")