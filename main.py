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
    # This section is the central hub for hooking into Discord's event stream.
    ############################################################################
    
    @bot.event
    async def on_message(message: discord.Message):
        """
        Handles all incoming messages for activity tracking and AI moderation.
        This consolidates logic previously in core/bot.py for consistency.
        """
        if message.author.bot or not message.guild:
            return

        # --- Activity Tracking ---
        # This now calls the fully implemented tracker for messages, replies, and mentions.
        if activity_tracker := bot.get_dependency('activity_tracker'):
            await activity_tracker.track_message_activity(message)
        
        # --- AI Moderation ---
        # This logic is moved from core/bot.py to keep all message handling in one place.
        try:
            from core.settings import bot_settings
            if not bot_settings.get("ai_enabled", False): return
            
            watch_scope = bot_settings.get("watch_scope", "specific_channels")
            watch_channels = bot_settings.get("watch_channels", [])
            
            if watch_scope == "specific_channels" and message.channel.id not in watch_channels:
                return
            
            if (ollama := bot.get_dependency('ollama')) and (logger := bot.get_dependency('logger')):
                analysis = await ollama.analyze_message(message.content, message.author.id, message.channel.id)
                if analysis.get('should_flag', False):
                    # This could also be expanded to create a Timeline event for AI flags.
                    await logger.log_flagged_message(
                        message.author.id, message.author.name, message.author.display_name,
                        message.content, message.created_at, message.jump_url,
                        confidence=analysis.get('confidence', 0), flags=analysis.get('flags', {}),
                        ai_explanation=analysis.get('reasoning', ''), channel_id=message.channel.id,
                        channel_name=message.channel.name
                    )
        except Exception as e:
            print(f"{Fore.RED}❌ AI moderation error in on_message: {e}{Style.RESET_ALL}")
            
        # --- Command Processing ---
        # This is essential for your slash commands to work.
        await bot.process_commands(message)

    @bot.event
    async def on_raw_message_delete(payload: discord.RawMessageDeleteEvent):
        """Handles ALL message deletions for both the deleted message log AND the timeline."""
        # This function remains exactly as it was in the last correct version.
        deleted_logger = bot.get_dependency('deleted_message_logger')
        audit_logger = bot.get_dependency('audit_logger')
        if not deleted_logger or not audit_logger:
            return

        await deleted_logger.log_raw_deleted_message(payload)

        try:
            guild = bot.get_guild(payload.guild_id)
            if not guild: return

            message_author = payload.cached_message.author if payload.cached_message else None
            deleter = None

            await asyncio.sleep(2)
            async for entry in guild.audit_logs(limit=5, action=discord.AuditLogAction.message_delete):
                if entry.extra.channel.id == payload.channel_id and entry.target.id == (message_author.id if message_author else 0):
                    deleter = entry.user
                    break
            
            if deleter:
                actor_data = {"id": str(deleter.id), "name": deleter.display_name, "avatar": str(deleter.display_avatar.url) if deleter.display_avatar else None}
            elif message_author:
                actor_data = {"id": str(message_author.id), "name": f"{message_author.display_name} (Self)", "avatar": str(message_author.display_avatar.url) if message_author.display_avatar else None}
            else:
                actor_data = {"id": None, "name": "Unknown", "avatar": None}

            target_data = {"id": str(message_author.id), "name": message_author.display_name, "avatar": str(message_author.display_avatar.url)} if message_author else None

            audit_logger.log_event(
                event_type="MESSAGE_DELETED", actor=actor_data, target=target_data,
                details={
                    "Channel": f"#{payload.cached_message.channel.name}" if payload.cached_message else "Unknown",
                    "Content": payload.cached_message.content if payload.cached_message and payload.cached_message.content else "[Content not available]",
                    "Message ID": str(payload.message_id)
                }, guild=guild
            )

            if deleter:
                await deleted_logger.update_log_with_deleter(message_id=payload.message_id, deleter_id=deleter.id, deleter_name=deleter.display_name)
        except discord.Forbidden: pass
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️  Could not process timeline log for deleted message: {e}{Style.RESET_ALL}")

    @bot.event
    async def on_member_join(member):
        """Logs when a user joins the server for the Timeline and join/leave history."""
        audit_logger = bot.get_dependency('audit_logger')
        activity_tracker = bot.get_dependency('activity_tracker')
        
        if audit_logger:
            actor_data = {"id": str(member.id), "name": member.display_name, "avatar": str(member.display_avatar.url)}
            account_age_days = (discord.utils.utcnow() - member.created_at).days
            audit_logger.log_event(
                event_type="MEMBER_JOINED", actor=actor_data,
                details={"Username": member.name, "Account Age": f"{account_age_days} days", "Total Members": member.guild.member_count},
                guild=member.guild
            )
        if activity_tracker:
            await activity_tracker.track_member_join_leave(member, 'join')

    @bot.event
    async def on_member_remove(member):
        """Logs kicks or leaves for the Timeline and join/leave history."""
        audit_logger = bot.get_dependency('audit_logger')
        activity_tracker = bot.get_dependency('activity_tracker')

        if activity_tracker:
            await activity_tracker.track_member_join_leave(member, 'leave')

        if audit_logger:
            guild = member.guild
            actor = None
            entry = None
            await asyncio.sleep(2)
            try:
                async for log_entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.kick):
                    if log_entry.target.id == member.id:
                        actor = log_entry.user
                        entry = log_entry
                        break
            except discord.Forbidden: actor = None

            if actor:
                event_type = "MEMBER_KICKED"
                actor_data = {"id": str(actor.id), "name": actor.display_name, "avatar": str(actor.display_avatar.url)}
                target_data = {"id": str(member.id), "name": member.display_name, "avatar": str(member.display_avatar.url)}
                details = {"Reason": entry.reason or "No reason provided."}
            else:
                event_type = "MEMBER_LEFT"
                actor_data = {"id": str(member.id), "name": member.display_name, "avatar": str(member.display_avatar.url)}
                target_data = None
                details = {"Username": member.name, "Total Members": guild.member_count}
            audit_logger.log_event(event_type=event_type, actor=actor_data, target=target_data, details=details, guild=guild)

    @bot.event
    async def on_member_ban(guild, user):
        """Logs member bans for the Timeline."""
        audit_logger = bot.get_dependency('audit_logger')
        if not audit_logger: return
        moderator, entry = None, None
        await asyncio.sleep(2)
        try:
            async for log_entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
                if log_entry.target.id == user.id:
                    moderator, entry = log_entry.user, log_entry
                    break
        except discord.Forbidden: pass
        actor_data = {"id": str(moderator.id) if moderator else None, "name": moderator.display_name if moderator else "Unknown", "avatar": str(moderator.display_avatar.url) if moderator and moderator.display_avatar else None}
        target_data = {"id": str(user.id), "name": user.display_name, "avatar": str(user.display_avatar.url) if hasattr(user, 'display_avatar') and user.display_avatar else None}
        audit_logger.log_event(event_type="MEMBER_BANNED", actor=actor_data, target=target_data, details={"Reason": entry.reason if entry else "No reason provided."}, guild=guild)

    @bot.event
    async def on_member_update(before, after):
        """Logs nickname changes for the Timeline."""
        audit_logger = bot.get_dependency('audit_logger')
        if not audit_logger: return
        if before.nick != after.nick:
            actor_data = {"id": str(after.id), "name": after.display_name, "avatar": str(after.display_avatar.url)}
            audit_logger.log_event(event_type="USER_NAME_CHANGED", actor=actor_data, details={"Change": "Nickname", "From": before.nick or "None", "To": after.nick or "None"}, guild=after.guild)

    @bot.event
    async def on_user_update(before, after):
        """Logs username changes for the Timeline."""
        audit_logger = bot.get_dependency('audit_logger')
        if not audit_logger: return
        if before.name != after.name:
            actor_data = {"id": str(after.id), "name": after.name, "avatar": str(after.avatar.url if after.avatar else '')}
            audit_logger.log_event(event_type="USER_NAME_CHANGED", actor=actor_data, details={"Change": "Username", "From": before.name, "To": after.name})

    @bot.event
    async def on_voice_state_update(member, before, after):
        """Tracks voice activity for the Cohorts page."""
        if activity_tracker := bot.get_dependency('activity_tracker'):
            await activity_tracker.track_voice_state_update(member, before, after)

    @bot.event
    async def on_raw_reaction_add(payload):
        """Tracks positive/negative reactions for the Cohorts page."""
        if activity_tracker := bot.get_dependency('activity_tracker'):
            await activity_tracker.track_reaction(payload)
    
    @bot.event
    async def on_raw_reaction_remove(payload):
        """Tracks positive/negative reactions for the Cohorts page."""
        if activity_tracker := bot.get_dependency('activity_tracker'):
            await activity_tracker.track_reaction(payload)

    ############################################################################
    # API AND BOT STARTUP
    ############################################################################
    
    initialize_api_dependencies(
        bot, deps['config'], deps['logger'], deps['ollama'],
        deps['moderation_manager'], deps['deleted_message_logger'],
        deps['activity_tracker'], deps['bot_settings'],
        deps['modstring_manager'], deps['audit_logger']
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