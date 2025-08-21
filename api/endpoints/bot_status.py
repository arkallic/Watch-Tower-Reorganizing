# api/endpoints/bot_status.py
from fastapi import APIRouter, HTTPException
from datetime import datetime

router = APIRouter(prefix="/bot", tags=["bot"])

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

@router.get("/status")
async def get_bot_status():
    """Get detailed bot status and performance metrics"""
    try:
        if not bot:
            return {"error": "Bot not initialized", "ready": False}
        
        if not bot.is_ready():
            return {"ready": False, "status": "connecting"}
        
        guild = bot.guilds[0] if bot.guilds else None
        
        return {
            "ready": True,
            "latency": round(bot.latency * 1000, 2),
            "guilds": len(bot.guilds),
            "users": sum(guild.member_count for guild in bot.guilds),
            "uptime": None,  # Will be calculated from bot start time
            "status": "online",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/guild/info")
async def get_guild_info():
    """Get detailed information about the connected guild"""
    try:
        if not bot or not bot.guilds:
            raise HTTPException(status_code=404, detail="No guild connected")
        
        guild = bot.guilds[0]
        
        return {
            "id": guild.id,
            "name": guild.name,
            "member_count": guild.member_count,
            "text_channels": len(guild.text_channels),
            "voice_channels": len(guild.voice_channels),
            "categories": len(guild.categories),
            "roles": len(guild.roles),
            "created_at": guild.created_at.isoformat(),
            "features": guild.features,
            "verification_level": str(guild.verification_level),
            "icon_url": str(guild.icon.url) if guild.icon else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))