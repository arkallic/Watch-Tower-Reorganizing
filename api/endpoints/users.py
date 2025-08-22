# api/endpoints/users.py
from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from typing import List, Dict, Any
import discord

router = APIRouter(prefix="/api", tags=["users"])

# Global dependencies - will be injected
bot = None
moderation_manager = None
deleted_message_logger = None
activity_tracker = None
logger = None

def initialize_dependencies(bot_instance, moderation_manager_instance, 
                          deleted_message_logger_instance, activity_tracker_instance, logger_instance=None):
    """Initialize dependencies for this endpoint module"""
    global bot, moderation_manager, deleted_message_logger, activity_tracker, logger
    bot = bot_instance
    moderation_manager = moderation_manager_instance
    deleted_message_logger = deleted_message_logger_instance
    activity_tracker = activity_tracker_instance
    logger = logger_instance

def calculate_user_risk(user_cases: List[Dict], user_flags: List[Dict], user_deletions: List[Dict]) -> Dict[str, Any]:
    """
    Calculates a comprehensive risk score and level for a user, ensuring consistency.
    This new logic incorporates cases, AI flags, and deletions with weighted values.
    MATCHES ORIGINAL API_calls.py exactly
    """
    now = datetime.now()
    thirty_days_ago = now - timedelta(days=30)
    
    # Define weights for actions and events
    severity_weights = {"Low": 1, "Medium": 3, "High": 8, "Critical": 20}
    action_weights = {"warn": 2, "timeout": 5, "kick": 10, "ban": 25, "mod_note": 0.5}
    event_weights = {"ai_flag": 0.5, "deletion": 0.2}
    recency_multiplier = 2.5 # Recent events are more significant

    risk_score = 0.0
    recent_cases_count = 0

    # 1. Calculate score from cases
    for case in user_cases:
        score_increase = severity_weights.get(case.get("severity", "Low"), 1)
        score_increase += action_weights.get(case.get("action_type", ""), 0)
        
        try:
            case_time = datetime.fromisoformat(case.get("created_at").replace('Z', '+00:00')).replace(tzinfo=None)
            if case_time > thirty_days_ago:
                score_increase *= recency_multiplier
                recent_cases_count += 1
        except (ValueError, TypeError):
            pass # Ignore cases with invalid timestamps
        risk_score += score_increase

    # 2. Calculate score from AI flags and deletions
    try:
        recent_flags = len([f for f in user_flags if datetime.fromisoformat(f.get("timestamp")).replace(tzinfo=None) > thirty_days_ago])
        risk_score += len(user_flags) * event_weights["ai_flag"]
        risk_score += recent_flags * event_weights["ai_flag"] * recency_multiplier
    except:
        pass

    # Assuming deleted_message_logger stores 'deleted_at'
    try:
        recent_deletions = len([d for d in user_deletions if datetime.fromisoformat(d.get("deleted_at")).replace(tzinfo=None) > thirty_days_ago])
        risk_score += len(user_deletions) * event_weights["deletion"]
        risk_score += recent_deletions * event_weights["deletion"] * recency_multiplier
    except:
        pass

    # 3. Determine final risk level
    risk_score = round(risk_score)
    if risk_score >= 25:
        risk_level = "Critical"
    elif risk_score >= 10:
        risk_level = "High"
    elif risk_score >= 4:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    return {"score": risk_score, "level": risk_level, "recent_cases": recent_cases_count}

@router.get("/users")
async def get_all_users():
    """Get all server members with consistent moderation data - MATCHES ORIGINAL API_calls.py exactly"""
    if not (bot and bot.guilds):
        raise HTTPException(status_code=503, detail="Bot is not connected to any servers")
    
    guild = bot.guilds[0]
    all_cases = moderation_manager.get_all_cases()
    all_flags = logger.get_all_flags() if logger and hasattr(logger, 'get_all_flags') else []
    all_deletions = deleted_message_logger.get_all_deletions() if deleted_message_logger and hasattr(deleted_message_logger, 'get_all_deletions') else []

    users_data = []
    for member in guild.members:
        user_id = member.id
        
        # --- THIS IS THE FIX ---
        # Ensure we compare strings to strings for consistency
        user_cases = [c for c in all_cases if str(c.get("user_id")) == str(user_id)]
        # --- END OF FIX ---

        user_flags = [f for f in all_flags if str(f.get("user_id")) == str(user_id)]
        user_deletions = [d for d in all_deletions if str(d.get("author_id")) == str(user_id)]

        risk_info = calculate_user_risk(user_cases, user_flags, user_deletions)

        users_data.append({
            "user_id": str(user_id),
            "username": member.name, 
            "display_name": member.display_name, 
            "discriminator": member.discriminator,
            "avatar": member.display_avatar.url, 
            "bot": member.bot, 
            "status": str(member.status),
            "joined_at": member.joined_at.isoformat() if member.joined_at else None,
            "created_at": member.created_at.isoformat(),
            "total_cases": len(user_cases),
            "open_cases": len([c for c in user_cases if c.get("status") == "Open"]),
            "recent_cases": risk_info["recent_cases"],
            "risk_score": risk_info["score"], 
            "risk_level": risk_info["level"],
            "total_flags": len(user_flags), 
            "total_deletions": len(user_deletions),
            "action_breakdown": {
                "warns": len([c for c in user_cases if c.get("action_type") == "warn"]),
                "timeouts": len([c for c in user_cases if c.get("action_type") == "timeout"]),
                "kicks": len([c for c in user_cases if c.get("action_type") == "kick"]),
                "bans": len([c for c in user_cases if c.get("action_type") == "ban"]),
                "mod_notes": len([c for c in user_cases if c.get("action_type") == "mod_note"])
            },
            "roles": [{"name": r.name, "color": str(r.color)} for r in member.roles if r.name != "@everyone"],
            "top_role": {"name": member.top_role.name, "color": str(member.top_role.color)} if member.top_role else None,
            "account_age_days": (datetime.now() - member.created_at.replace(tzinfo=None)).days,
            "server_tenure_days": (datetime.now() - member.joined_at.replace(tzinfo=None)).days if member.joined_at else 0,
        })
    return {"users": users_data}

@router.get("/users/{user_id}")
async def get_user_details(user_id: int):
    """Get detailed user information with consistent risk calculation - MATCHES ORIGINAL API_calls.py exactly"""
    if not bot or not bot.guilds: 
        raise HTTPException(status_code=503, detail="Bot is not connected")
    
    guild = bot.guilds[0]
    member = guild.get_member(user_id)
    if not member: 
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    user_cases = [c for c in moderation_manager.get_all_cases() if c.get("user_id") == user_id]
    all_flags = logger.get_all_flags() if logger and hasattr(logger, 'get_all_flags') else []
    user_flags = [f for f in all_flags if f.get("user_id") == user_id]
    all_deletions = deleted_message_logger.get_all_deletions() if deleted_message_logger and hasattr(deleted_message_logger, 'get_all_deletions') else []
    user_deletions = [d for d in all_deletions if d.get("author_id") == user_id]

    risk_info = calculate_user_risk(user_cases, user_flags, user_deletions)

    return {
        "user_id": str(user_id), 
        "username": member.name, 
        "display_name": member.display_name, 
        "discriminator": member.discriminator,
        "avatar": member.display_avatar.url, 
        "bot": member.bot, 
        "status": str(member.status),
        "joined_at": member.joined_at.isoformat() if member.joined_at else None,
        "created_at": member.created_at.isoformat(),
        "account_age_days": (datetime.now() - member.created_at.replace(tzinfo=None)).days,
        "server_tenure_days": (datetime.now() - member.joined_at.replace(tzinfo=None)).days if member.joined_at else 0,
        "risk_level": risk_info["level"], 
        "risk_score": risk_info["score"],
        "cases": user_cases,
        "stats": {
            "total_cases": len(user_cases), 
            "open_cases": len([c for c in user_cases if c.get("status") == "Open"]),
            "resolved_cases": len([c for c in user_cases if c.get("status") != "Open"]),
        },
        "total_flags": len(user_flags), 
        "total_deletions": len(user_deletions),
        "action_breakdown": {
            "warns": len([c for c in user_cases if c.get("action_type") == "warn"]),
            "timeouts": len([c for c in user_cases if c.get("action_type") == "timeout"]),
            "kicks": len([c for c in user_cases if c.get("action_type") == "kick"]),
            "bans": len([c for c in user_cases if c.get("action_type") == "ban"]),
            "mod_notes": len([c for c in user_cases if c.get("action_type") == "mod_note"])
        },
        "roles": [{"name": r.name, "color": str(r.color)} for r in member.roles if r.name != "@everyone"],
        "permissions": {perm: value for perm, value in member.guild_permissions if perm in ['administrator', 'manage_messages', 'kick_members', 'ban_members']}
    }