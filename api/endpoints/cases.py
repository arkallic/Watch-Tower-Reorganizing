# api/endpoints/cases.py
from fastapi import APIRouter, HTTPException
from typing import Optional
import json
from pathlib import Path
from datetime import datetime
import discord

router = APIRouter(prefix="/api/cases", tags=["cases"])

# Global dependencies
moderation_manager = None
bot = None

def initialize_dependencies(moderation_manager_instance, bot_instance):
    global moderation_manager, bot
    moderation_manager = moderation_manager_instance
    bot = bot_instance

@router.get("/")
async def get_all_cases():
    """Get all moderation cases"""
    try:
        cases = moderation_manager.get_all_cases()
        return {"cases": cases}
    except Exception as e:
        return {"error": str(e), "cases": []}

@router.get("/{user_id}/{case_number}")
async def get_specific_case(user_id: int, case_number: int):
    """Get a specific case by user ID and case number"""
    try:
        case = moderation_manager.get_user_case_by_number(user_id, case_number)
        if case:
            return {"case": case}
        else:
            return {"error": "Case not found", "case": None}
    except Exception as e:
        return {"error": str(e), "case": None}

@router.put("/{user_id}/{case_number}")
async def update_case(user_id: int, case_number: int, updates: dict):
    """Update a specific case"""
    try:
        success = moderation_manager.update_case(user_id, case_number, updates)
        return {"success": success}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.delete("/{user_id}/{case_number}")
async def delete_case(user_id: int, case_number: int):
    """Delete a specific case"""
    try:
        success = moderation_manager.delete_case(user_id, case_number)
        return {"success": success}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/enhanced")
async def get_cases_enhanced():
    """Get all cases with enhanced user information including avatars - MATCHES ORIGINAL API_calls.py"""
    try:
        # Use the exact same path as original - this is critical!
        cases_path = Path("cases/user_moderation_data.json")
        if not cases_path.exists():
            return {"cases": []}
        
        with open(cases_path, 'r', encoding='utf-8') as f:
            user_cases = json.load(f)
        
        all_cases = []
        
        # Get Discord bot instance for user lookups - exact same logic as original
        guild = None
        if bot and bot.is_ready() and bot.guilds:
            guild = bot.guilds[0]
        
        for user_id, user_data in user_cases.items():
            # Try to get Discord user info - exact same logic as original
            discord_user = None
            user_avatar_url = None
            
            if guild:
                try:
                    discord_user = guild.get_member(int(user_id))
                    if discord_user:
                        user_avatar_url = str(discord_user.display_avatar.url)
                except:
                    try:
                        discord_user = await bot.fetch_user(int(user_id))
                        if discord_user:
                            user_avatar_url = str(discord_user.display_avatar.url)
                    except:
                        pass
            
            for case in user_data.get('cases', []):
                # CRITICAL: Use exact same field mapping as original API_calls.py
                case_data = {
                    'case_number': case.get('case_number'),
                    'user_id': user_id,
                    'username': case.get('username') or (discord_user.name if discord_user else 'Unknown'),
                    'display_name': case.get('display_name') or (discord_user.display_name if discord_user else None),
                    'user_avatar_url': user_avatar_url,
                    'action_type': case.get('action_taken', 'Unknown'),  # Note: 'action_taken' not 'action_type'
                    'moderator_id': case.get('moderator_id'),
                    'moderator_name': case.get('moderator_name', 'Unknown'),
                    'reason': case.get('reason', ''),
                    'internal_comment': case.get('internal_comment', ''),
                    'severity': case.get('severity', 'Low'),
                    'status': case.get('status', 'Open'),
                    'created_at': case.get('timestamp'),  # Note: 'timestamp' not 'created_at'
                    'resolved_at': case.get('resolved_at'),
                    'duration': case.get('duration'),
                    'dm_sent': case.get('dm_sent', False),
                    'resolvable': case.get('resolvable', 'Yes'),
                    'tags': case.get('tags', []),
                    'flagged_message': case.get('flagged_message'),
                    'message_history': case.get('message_history', []),
                    'attachments': case.get('attachments', []),
                    'resolution_method': case.get('resolution_method'),
                    'resolution_comment': case.get('resolution_comment'),
                    'resolved_by_name': case.get('resolved_by_name')
                }
                all_cases.append(case_data)
        
        # Sort by case number (newest first) - exact same as original
        all_cases.sort(key=lambda x: x.get('case_number', 0), reverse=True)
        
        return {"cases": all_cases}
        
    except Exception as e:
        return {"error": str(e)}, 500