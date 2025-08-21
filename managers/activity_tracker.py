# managers/activity_tracker.py
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import os
from colorama import Fore, Style

class ActivityTracker:
    def __init__(self):
        # Get the script directory - point to root level
        self.script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Go up two levels
        self.data_path = os.path.join(self.script_dir, "data")
        os.makedirs(self.data_path, exist_ok=True)
        
        # Activity tracking files
        self.message_activity_file = os.path.join(self.data_path, "message_activity.json")
        self.voice_activity_file = os.path.join(self.data_path, "voice_activity.json")
        self.reaction_activity_file = os.path.join(self.data_path, "reaction_activity.json")
        self.member_activity_file = os.path.join(self.data_path, "member_activity.json")
        
        # In-memory caches for performance
        self.activity_cache = {}
        self.cache_ttl = 300  # 5 minutes
        
    async def track_message_activity(self, user_id: int, channel_id: int, guild_id: int, 
                                   message_length: int, has_attachments: bool = False,
                                   has_embeds: bool = False, mention_count: int = 0):
        """Track comprehensive message activity"""
        activity_data = {
            "user_id": user_id,
            "channel_id": channel_id,
            "guild_id": guild_id,
            "timestamp": datetime.now().isoformat(),
            "message_length": message_length,
            "has_attachments": has_attachments,
            "has_embeds": has_embeds,
            "mention_count": mention_count,
            "hour": datetime.now().hour,
            "day_of_week": datetime.now().weekday()
        }
        
        await self._append_activity_data(self.message_activity_file, activity_data)
        
    async def track_voice_activity(self, user_id: int, channel_id: int, guild_id: int,
                                 action: str, duration: Optional[int] = None):
        """Track voice channel activity"""
        activity_data = {
            "user_id": user_id,
            "channel_id": channel_id,
            "guild_id": guild_id,
            "action": action,  # "join", "leave", "move"
            "timestamp": datetime.now().isoformat(),
            "duration": duration
        }
        
        await self._append_activity_data(self.voice_activity_file, activity_data)
        
    async def track_reaction_activity(self, user_id: int, message_id: int, channel_id: int,
                                    emoji: str, action: str):
        """Track reaction activity"""
        activity_data = {
            "user_id": user_id,
            "message_id": message_id,
            "channel_id": channel_id,
            "emoji": emoji,
            "action": action,  # "add", "remove"
            "timestamp": datetime.now().isoformat()
        }
        
        await self._append_activity_data(self.reaction_activity_file, activity_data)
        
    async def track_member_activity(self, user_id: int, guild_id: int, action: str, **kwargs):
        """Track member-related activity"""
        activity_data = {
            "user_id": user_id,
            "guild_id": guild_id,
            "action": action,  # "join", "leave", "role_change"
            "timestamp": datetime.now().isoformat(),
            **kwargs
        }
        
        await self._append_activity_data(self.member_activity_file, activity_data)
    
    async def _append_activity_data(self, file_path: str, data: Dict[str, Any]):
        """Append activity data to file"""
        try:
            # Load existing data
            activities = []
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        activities = json.load(f)
                except (json.JSONDecodeError, FileNotFoundError):
                    activities = []
            
            # Add new data
            activities.append(data)
            
            # Keep only last 1000 entries per file
            if len(activities) > 1000:
                activities = activities[-1000:]
            
            # Save back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(activities, f, indent=2, ensure_ascii=False, default=str)
                
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️ Error tracking activity: {e}{Style.RESET_ALL}")
    
    def get_user_activity_summary(self, user_id: int, hours_back: int = 24) -> Dict[str, Any]:
        """Get activity summary for a user"""
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        summary = {
            "messages": 0,
            "voice_sessions": 0,
            "reactions": 0,
            "total_events": 0
        }
        
        try:
            # Check message activity
            if os.path.exists(self.message_activity_file):
                with open(self.message_activity_file, 'r', encoding='utf-8') as f:
                    activities = json.load(f)
                    for activity in activities:
                        if (activity.get("user_id") == user_id and
                            datetime.fromisoformat(activity.get("timestamp", "")) >= cutoff_time):
                            summary["messages"] += 1
            
            # Check voice activity
            if os.path.exists(self.voice_activity_file):
                with open(self.voice_activity_file, 'r', encoding='utf-8') as f:
                    activities = json.load(f)
                    for activity in activities:
                        if (activity.get("user_id") == user_id and
                            datetime.fromisoformat(activity.get("timestamp", "")) >= cutoff_time):
                            summary["voice_sessions"] += 1
            
            # Check reaction activity
            if os.path.exists(self.reaction_activity_file):
                with open(self.reaction_activity_file, 'r', encoding='utf-8') as f:
                    activities = json.load(f)
                    for activity in activities:
                        if (activity.get("user_id") == user_id and
                            datetime.fromisoformat(activity.get("timestamp", "")) >= cutoff_time):
                            summary["reactions"] += 1
            
            summary["total_events"] = summary["messages"] + summary["voice_sessions"] + summary["reactions"]
            
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️ Error getting activity summary: {e}{Style.RESET_ALL}")
        
        return summary