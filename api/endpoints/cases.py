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
        # Updated to read individual case files instead of consolidated file
        cases_dir = Path("cases")
        if not cases_dir.exists():
            print(f"❌ Bot API: Cases directory not found")
            return {"cases": []}
        
        print(f"🔍 Bot API: Reading individual case files from {cases_dir.absolute()}")
        
        all_cases = []
        case_files = list(cases_dir.glob("case_*.json"))
        print(f"📊 Bot API: Found {len(case_files)} case files")
        
        # Get Discord bot instance for user lookups
        guild = None
        if bot and bot.is_ready() and bot.guilds:
            guild = bot.guilds[0]
            print(f"✅ Bot API: Bot is ready, guild: {guild.name}")
        else:
            print(f"❌ Bot API: Bot not ready or no guilds")
        
        for case_file in case_files:
            try:
                print(f"📋 Bot API: Processing {case_file.name}")
                
                with open(case_file, 'r', encoding='utf-8') as f:
                    case = json.load(f)
                
                user_id = str(case.get('user_id'))
                
                # Try to get Discord user info for enhanced data
                discord_user = None
                user_avatar_url = case.get('user_avatar_url')  # Use existing if available
                
                if guild and not user_avatar_url:
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
                
                # Create enhanced case data with proper field mapping
                case_data = {
                    'case_number': case.get('case_number'),
                    'user_id': user_id,
                    'username': case.get('username') or (discord_user.name if discord_user else 'Unknown'),
                    'display_name': case.get('display_name') or (discord_user.display_name if discord_user else None),
                    'user_avatar_url': user_avatar_url,
                    'action_type': case.get('action_type', 'Unknown'),
                    'moderator_id': case.get('moderator_id'),
                    'moderator_name': case.get('moderator_name', 'Unknown'),
                    'reason': case.get('reason', ''),
                    'internal_comment': case.get('internal_comment', ''),
                    'severity': case.get('severity', 'Low'),
                    'status': case.get('status', 'Open'),
                    'created_at': case.get('created_at') or case.get('timestamp'),
                    'resolved_at': case.get('resolved_at'),
                    'duration': case.get('duration'),
                    'dm_sent': case.get('dm_sent', False),
                    'resolvable': case.get('resolvable', 'Yes'),
                    'tags': case.get('tags', []),
                    'flagged_message': case.get('flagged_message'),
                    'message_history': case.get('recent_messages', []),  # Note: using 'recent_messages'
                    'attachments': case.get('attachments', []),
                    'resolution_method': case.get('resolution_method'),
                    'resolution_comment': case.get('resolution_comment'),
                    'resolved_by_name': case.get('resolved_by_name')
                }
                all_cases.append(case_data)
                print(f"✅ Bot API: Added case #{case.get('case_number')} for user {user_id}")
                
            except Exception as e:
                print(f"❌ Bot API: Error processing {case_file.name}: {e}")
                continue
        
        print(f"📊 Bot API: Total cases processed: {len(all_cases)}")
        
        # Sort by case number (newest first)
        all_cases.sort(key=lambda x: x.get('case_number', 0), reverse=True)
        
        return {"cases": all_cases}
        
    except Exception as e:
        print(f"❌ Bot API: Error in get_cases_enhanced: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e), "cases": []}