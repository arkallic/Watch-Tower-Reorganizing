# api/endpoints/users.py
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
import discord

router = APIRouter(prefix="/api/users", tags=["users"])

# Global dependencies
bot = None
moderation_manager = None
deleted_message_logger = None
activity_tracker = None

def initialize_dependencies(bot_instance, moderation_manager_instance, 
                          deleted_message_logger_instance, activity_tracker_instance):
    global bot, moderation_manager, deleted_message_logger, activity_tracker
    bot = bot_instance
    moderation_manager = moderation_manager_instance
    deleted_message_logger = deleted_message_logger_instance
    activity_tracker = activity_tracker_instance

@router.get("/")
async def get_users(limit: int = Query(50, le=200), search: Optional[str] = None):
    """Get list of users with moderation data"""
    try:
        if not bot or not bot.guilds:
            return {"users": [], "total": 0}
        
        guild = bot.guilds[0]
        users_data = []
        
        # Get moderation data
        moderation_data = moderation_manager.user_data if moderation_manager else {}
        
        for member in guild.members[:limit]:
            if search and search.lower() not in member.display_name.lower():
                continue
            
            user_key = str(member.id)
            user_mod_data = moderation_data.get(user_key, {})
            
            user_info = {
                "id": member.id,
                "username": member.name,
                "display_name": member.display_name,
                "avatar_url": str(member.display_avatar.url),
                "joined_at": member.joined_at.isoformat() if member.joined_at else None,
                "roles": [role.name for role in member.roles[1:]],  # Exclude @everyone
                "moderation": {
                    "total_cases": user_mod_data.get("total_cases", 0),
                    "open_cases": user_mod_data.get("open_cases", 0),
                    "warns": user_mod_data.get("warns", 0),
                    "timeouts": user_mod_data.get("timeouts", 0),
                    "kicks": user_mod_data.get("kicks", 0),
                    "bans": user_mod_data.get("bans", 0),
                    "last_case_date": user_mod_data.get("last_case_date")
                }
            }
            users_data.append(user_info)
        
        return {
            "users": users_data,
            "total": len(users_data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}")
async def get_user_details(user_id: int):
    """Get detailed information about a specific user"""
    try:
        if not bot or not bot.guilds:
            raise HTTPException(status_code=404, detail="No guild connected")
        
        guild = bot.guilds[0]
        member = guild.get_member(user_id)
        
        if not member:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get moderation data
        user_key = str(user_id)
        user_mod_data = moderation_manager.user_data.get(user_key, {}) if moderation_manager else {}
        
        # Get activity data
        activity_data = {}
        if activity_tracker:
            activity_data = activity_tracker.get_user_activity(user_id)
        
        return {
            "id": member.id,
            "username": member.name,
            "display_name": member.display_name,
            "avatar_url": str(member.display_avatar.url),
            "joined_at": member.joined_at.isoformat() if member.joined_at else None,
            "created_at": member.created_at.isoformat(),
            "roles": [{"id": role.id, "name": role.name, "color": role.color.value} for role in member.roles[1:]],
            "permissions": [perm for perm, value in member.guild_permissions if value],
            "moderation": user_mod_data,
            "activity": activity_data,
            "cases": user_mod_data.get("cases", [])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))