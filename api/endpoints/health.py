# api/endpoints/health.py
from fastapi import APIRouter, HTTPException
from datetime import datetime

router = APIRouter(tags=["health"])

# Global dependencies
bot = None
ollama = None
modstring_manager = None
activity_tracker = None
moderation_manager = None

def initialize_dependencies(bot_instance, ollama_instance, modstring_manager_instance, 
                          activity_tracker_instance, moderation_manager_instance):
    global bot, ollama, modstring_manager, activity_tracker, moderation_manager
    bot = bot_instance
    ollama = ollama_instance
    modstring_manager = modstring_manager_instance
    activity_tracker = activity_tracker_instance
    moderation_manager = moderation_manager_instance

@router.get("/health")
async def health_check():
    """Simple health check endpoint for external monitoring"""
    try:
        bot_ready = bot.is_ready() if bot else False
        return {
            "status": "healthy" if bot_ready else "degraded",
            "bot_ready": bot_ready,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/")
async def comprehensive_health_check():
    """Comprehensive health check endpoint"""
    try:
        bot_ready = bot.is_ready() if bot else False
        guild_connected = bool(bot.guilds) if bot_ready else False
        
        # Test AI connection
        ai_connected = False
        try:
            ai_connected = await ollama.check_connection() if ollama else False
        except:
            ai_connected = False
        
        # Test ModString connection
        modstring_connected = modstring_manager.enabled if modstring_manager else False
        
        return {
            "status": "healthy" if bot_ready and guild_connected else "degraded",
            "bot_ready": bot_ready,
            "guild_connected": guild_connected,
            "guilds": len(bot.guilds) if bot else 0,
            "latency": round(bot.latency * 1000, 2) if bot_ready else 0,
            "services": {
                "discord": bot_ready,
                "ai_moderation": ai_connected,
                "modstring_integration": modstring_connected,
                "activity_tracking": activity_tracker is not None,
                "case_management": moderation_manager is not None
            },
            "integrations": {
                "active_modstrings": len(modstring_manager.active_modstrings) if modstring_manager else 0,
                "word_lists": len(modstring_manager.word_lists) if modstring_manager else 0,
                "last_modstring_sync": modstring_manager.last_sync.isoformat() if modstring_manager and modstring_manager.last_sync else None
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))