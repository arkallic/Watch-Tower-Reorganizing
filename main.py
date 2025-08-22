import os
import asyncio
from colorama import Fore, Style
import discord

from core.startup import ApplicationStartup
from core.dependency_container import DependencyContainer
from core.bot import WatchTowerBot
from api.api_app import initialize_api_dependencies
from api.api_server import start_api_server

async def main():
    """Main application entry point"""
    print(f"{Fore.CYAN}🏗️  Starting Watch Tower Bot...{Style.RESET_ALL}")
    
    ApplicationStartup.initialize_system()
    container = DependencyContainer()
    container.initialize_all_dependencies()
    deps = container.get_all_dependencies()
    
    bot = WatchTowerBot()
    container.initialize_bot_dependent_components(bot)
    bot.inject_dependencies(deps)
    
    ############################################################################
    # BOT EVENT LISTENERS
    ############################################################################
    
    @bot.event
    async def on_raw_message_delete(payload: discord.RawMessageDeleteEvent):
        """
        Handles ALL message deletions and checks audit log to find the deleter.
        This is the single source of truth for deleted message logging.
        """
        # We need the logger dependency to do anything
        if not (deleted_logger := bot.get_dependency('deleted_message_logger')):
            return

        # Log the deletion immediately from the payload data
        await deleted_logger.log_raw_deleted_message(payload)

        # Now, try to find out WHO deleted it from the audit log
        await asyncio.sleep(2) # Wait for audit log to populate
        
        guild = bot.get_guild(payload.guild_id)
        if not guild:
            return

        try:
            # We look for a "message_delete" action in the audit log.
            async for entry in guild.audit_logs(limit=5, action=discord.AuditLogAction.message_delete):
                # The entry's `target` will be the user whose message was deleted.
                # The entry's `user` is the moderator who performed the deletion.
                # We match based on the channel the deletion happened in.
                if entry.extra.channel.id == payload.channel_id:
                    # We found a log of a mod deleting a message in this channel.
                    # Now, we update our existing log entry with the moderator's name.
                    await deleted_logger.update_log_with_deleter(
                        message_id=payload.message_id,
                        deleter_id=entry.user.id,
                        deleter_name=entry.user.display_name
                    )
                    # We found the entry, no need to keep searching.
                    return
        except discord.Forbidden:
            # This is not an error, just means the bot can't check the audit log.
            pass
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️  Could not process audit log for deleted message: {e}{Style.RESET_ALL}")

    ############################################################################
    # API AND BOT STARTUP
    ############################################################################
    
    initialize_api_dependencies(
        bot, deps['config'], deps['logger'], deps['ollama'],
        deps['moderation_manager'], deps['deleted_message_logger'],
        deps['activity_tracker'], deps['bot_settings'],
        deps['modstring_manager']
    )
    
    start_api_server()
    
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print(f"{Fore.RED}❌ DISCORD_TOKEN not found in environment variables{Style.RESET_ALL}")
        return
    
    try:
        await bot.start(token)
    except KeyboardInterrupt:
        await bot.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}👋 Watch Tower Bot stopped{Style.RESET_ALL}")