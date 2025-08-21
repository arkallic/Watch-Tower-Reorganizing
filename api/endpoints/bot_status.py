# api/endpoints/bot_status.py
from fastapi import APIRouter, HTTPException
from datetime import datetime
import discord

router = APIRouter(tags=["bot"])

# Global dependencies - will be injected
bot = None
logger = None

def initialize_dependencies(bot_instance, logger_instance):
    global bot, logger
    bot = bot_instance
    logger = logger_instance

@router.get("/")
async def api_root():
    """API root endpoint with service information"""
    return {
        "message": "Watch Tower Bot API",
        "version": "2.0.0",
        "status": "online",
        "bot_ready": bot.is_ready() if bot else False,
        "endpoints": {
            "health": "/health",
            "bot_status": "/bot/status",
            "guild_info": "/bot/guild/info",
            "moderators": "/moderators",
            "users": "/api/users",
            "cases": "/api/cases",
            "stats": "/stats/*",
            "system": "/system/*"
        },
        "timestamp": datetime.now().isoformat()
    }

@router.get("/bot/status")
async def get_bot_status():
    """Get comprehensive bot status information"""
    try:
        if not bot or not bot.is_ready():
            return {"error": "Bot is not ready"}
            
        guild = bot.guilds[0] if bot.guilds else None
        
        # Test external connections
        try:
            ollama_status = await ollama.check_connection() if 'ollama' in globals() else False
        except:
            ollama_status = False
        
        # Get bot uptime
        uptime_seconds = 0
        if hasattr(bot, 'ready_time'):
            uptime_seconds = (datetime.now() - bot.ready_time).total_seconds()
        
        return {
            "bot_user": {
                "id": str(bot.user.id),
                "name": bot.user.name,
                "discriminator": bot.user.discriminator,
                "avatar_url": str(bot.user.avatar.url) if bot.user.avatar else None
            },
            "connection": {
                "status": "online",
                "latency": round(bot.latency * 1000, 2),
                "uptime_seconds": uptime_seconds,
                "guild_connected": guild is not None
            },
            "guild_info": {
                "id": str(guild.id),
                "name": guild.name,
                "member_count": guild.member_count,
                "channel_count": len(guild.channels),
                "role_count": len(guild.roles)
            } if guild else None,
            "integrations": {
                "ollama_connected": ollama_status,
                "config_loaded": True,
                "modstring_enabled": False
            },
            "permissions": {
                "administrator": guild.me.guild_permissions.administrator if guild else False,
                "manage_messages": guild.me.guild_permissions.manage_messages if guild else False,
                "kick_members": guild.me.guild_permissions.kick_members if guild else False,
                "ban_members": guild.me.guild_permissions.ban_members if guild else False
            } if guild else {},
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"error": f"Failed to get bot status: {str(e)}"}
    

@router.get("/bot/guild/info")
async def get_guild_info():
    """Get detailed guild information"""
    try:
        if not bot or not bot.is_ready() or not bot.guilds:
            return {"error": "Bot not connected to any guilds"}
        
        guild = bot.guilds[0]
        
        # Categorize channels
        text_channels = []
        voice_channels = []
        categories = []
        
        for channel in guild.channels:
            try:
                if isinstance(channel, discord.TextChannel):
                    text_channels.append({
                        "id": str(channel.id),
                        "name": channel.name,
                        "type": "text",
                        "category": channel.category.name if channel.category else None,
                        "category_id": str(channel.category.id) if channel.category else None,
                        "position": channel.position,
                        "nsfw": getattr(channel, 'nsfw', False),
                        "topic": channel.topic,
                        "slowmode_delay": channel.slowmode_delay
                    })
                elif isinstance(channel, discord.VoiceChannel):
                    voice_channels.append({
                        "id": str(channel.id),
                        "name": channel.name,
                        "type": "voice",
                        "category": channel.category.name if channel.category else None,
                        "category_id": str(channel.category.id) if channel.category else None,
                        "user_limit": getattr(channel, 'user_limit', 0),
                        "bitrate": channel.bitrate,
                        "connected_users": len(channel.members)
                    })
                elif isinstance(channel, discord.CategoryChannel):
                    categories.append({
                        "id": str(channel.id),
                        "name": channel.name,
                        "position": channel.position,
                        "channel_count": len(channel.channels)
                    })
            except Exception:
                continue
        
        # Get role information
        roles = []
        for role in guild.roles:
            try:
                if role.name != "@everyone":
                    roles.append({
                        "id": str(role.id),
                        "name": role.name,
                        "color": str(role.color),
                        "position": role.position,
                        "mentionable": role.mentionable,
                        "hoisted": role.hoist,
                        "managed": role.managed,
                        "member_count": len(role.members),
                        "permissions": role.permissions.value
                    })
            except Exception:
                continue
        
        return {
            "guild": {
                "id": str(guild.id),
                "name": guild.name,
                "description": guild.description,
                "icon_url": str(guild.icon.url) if guild.icon else None,
                "banner_url": str(guild.banner.url) if guild.banner else None,
                "owner_id": str(guild.owner_id),
                "created_at": guild.created_at.isoformat(),
                "verification_level": str(guild.verification_level),
                "explicit_content_filter": str(guild.explicit_content_filter),
                "features": list(guild.features),
                "premium_tier": guild.premium_tier,
                "premium_subscription_count": guild.premium_subscription_count or 0,
                "max_members": guild.max_members,
                "max_presences": guild.max_presences
            },
            "channels": {
                "text_channels": text_channels,
                "voice_channels": voice_channels,
                "categories": categories,
                "total_channels": len(text_channels) + len(voice_channels),
                "rules_channel": guild.rules_channel.name if guild.rules_channel else None,
                "system_channel": guild.system_channel.name if guild.system_channel else None,
                "afk_channel": guild.afk_channel.name if guild.afk_channel else None
            },
            "roles": roles,
            "emojis": {
                "total": len(guild.emojis),
                "static": len([e for e in guild.emojis if not e.animated]),
                "animated": len([e for e in guild.emojis if e.animated])
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"error": f"Failed to fetch guild info: {str(e)}"}