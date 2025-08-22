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
    
    def get_channel_message_counts(self, days_back: int = 30) -> Dict[str, int]:
        """
        Reads the message activity log and returns a dictionary mapping
        channel_id to its message count over a given period.
        """
        counts = {}
        if not os.path.exists(self.message_activity_file):
            return counts

        cutoff_date = datetime.now() - timedelta(days=days_back)

        try:
            with open(self.message_activity_file, 'r', encoding='utf-8') as f:
                activities = json.load(f)
            
            for activity in activities:
                try:
                    timestamp = datetime.fromisoformat(activity.get("timestamp", ""))
                    if timestamp >= cutoff_date:
                        channel_id = str(activity.get("channel_id"))
                        if channel_id:
                            counts[channel_id] = counts.get(channel_id, 0) + 1
                except (ValueError, TypeError):
                    continue
        except (json.JSONDecodeError, IOError) as e:
            print(f"{Fore.YELLOW}⚠️  Could not read activity file for counting: {e}{Style.RESET_ALL}")

        return counts

    def get_user_profile_activity(self, user_id: int, days_back: int = 365) -> Dict[str, Any]:
        """
        Generates a comprehensive activity profile for a single user,
        including heatmap data, top channels, and summary stats.
        """
        summary = {
            "message_count_30d": 0,
            "voice_minutes_30d": 0,
            "reactions_30d": 0,
            "top_channels": {},
            "heatmap_data": {}
        }
        
        cutoff_30d = datetime.now() - timedelta(days=30)
        cutoff_year = datetime.now() - timedelta(days=days_back)

        # Process Message Activity
        try:
            with open(self.message_activity_file, 'r', encoding='utf-8') as f:
                activities = json.load(f)
            
            user_messages = [a for a in activities if a.get("user_id") == user_id]

            for msg in user_messages:
                ts = datetime.fromisoformat(msg.get("timestamp", ""))
                if ts >= cutoff_year:
                    date_str = ts.strftime('%Y-%m-%d')
                    summary["heatmap_data"][date_str] = summary["heatmap_data"].get(date_str, 0) + 1

                if ts >= cutoff_30d:
                    summary["message_count_30d"] += 1
                    ch_id = str(msg.get("channel_id"))
                    if ch_id:
                        summary["top_channels"][ch_id] = summary["top_channels"].get(ch_id, 0) + 1
        except (IOError, json.JSONDecodeError):
            pass # File might not exist or be empty, which is fine

        # You can add similar processing for voice and reactions if needed
        
        return summary


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