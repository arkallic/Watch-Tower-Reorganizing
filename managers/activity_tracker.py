import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import os
from colorama import Fore, Style
from collections import Counter
import discord # Added for type hinting

class ActivityTracker:
    ############################################################################
    # INITIALIZATION & FILE SETUP
    ############################################################################

    def __init__(self):
        """Initializes the tracker, defines all log file paths, and sets up caches."""
        self.script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_path = os.path.join(self.script_dir, "data")
        os.makedirs(self.data_path, exist_ok=True)
        
        # Define paths for all activity log files
        self.message_activity_file = os.path.join(self.data_path, "message_activity.json")
        self.voice_activity_file = os.path.join(self.data_path, "voice_activity.json")
        self.reaction_activity_file = os.path.join(self.data_path, "reaction_activity.json")
        self.member_activity_file = os.path.join(self.data_path, "member_activity.json")
        self.social_activity_file = os.path.join(self.data_path, "social_activity.json")
        
        # In-memory cache for tracking active voice sessions to calculate duration
        self.voice_sessions = {}

    async def _append_activity_data(self, file_path: str, data: Dict[str, Any]):
        """A generic helper to safely append a new entry to a JSON log file."""
        try:
            activities = []
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        activities = json.load(f)
                except (json.JSONDecodeError, FileNotFoundError):
                    activities = []
            
            activities.append(data)
            
            # Simple log rotation to keep files from growing infinitely
            if len(activities) > 5000:
                activities = activities[-5000:]
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(activities, f, indent=2, ensure_ascii=False, default=str)
                
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️ Error in _append_activity_data for {os.path.basename(file_path)}: {e}{Style.RESET_ALL}")

    ############################################################################
    # CORE EVENT TRACKING METHODS (Called by the bot's event listeners)
    ############################################################################

    async def track_message_activity(self, message: discord.Message):
        """Tracks basic message events for trend analysis and social interactions for graphing."""
        if not message.guild: return

        # Log basic activity for volume and trend analysis
        basic_activity = {
            "user_id": message.author.id,
            "channel_id": message.channel.id,
            "timestamp": datetime.now().isoformat()
        }
        await self._append_activity_data(self.message_activity_file, basic_activity)

        # If there's a reply or mention, log it to the dedicated social graph log
        if message.reference or message.mentions:
            replied_to_author = None
            if message.reference and isinstance(message.reference.resolved, discord.Message):
                replied_to_author = message.reference.resolved.author.id

            social_activity = {
                "actor_user_id": message.author.id,
                "timestamp": datetime.now().isoformat(),
                "replied_to_user_id": replied_to_author,
                "mentioned_user_ids": [m.id for m in message.mentions if not m.bot]
            }
            await self._append_activity_data(self.social_activity_file, social_activity)

    async def track_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        """Tracks when a user joins or leaves a voice channel to calculate session duration."""
        user_id = member.id
        now = datetime.now()

        if after.channel and not before.channel:
            self.voice_sessions[user_id] = now
        
        elif not after.channel and before.channel:
            if user_id in self.voice_sessions:
                duration_seconds = (now - self.voice_sessions.pop(user_id)).total_seconds()
                if duration_seconds > 60:
                    await self._append_activity_data(self.voice_activity_file, {
                        "user_id": user_id, "duration_minutes": round(duration_seconds / 60), "timestamp": now.isoformat()
                    })

    async def track_reaction(self, payload: discord.RawReactionActionEvent):
        """Tracks reactions and categorizes their sentiment."""
        positive_emojis = ['👍', '❤️', '😂', '🎉', '👏', '💯', '🔥', '✅', '✨', '🤩']
        negative_emojis = ['😠', '👎', '🤢', '😡', '🤬', '😑', '😒']
        
        emoji_str = str(payload.emoji)
        sentiment = 'neutral'
        if emoji_str in positive_emojis: sentiment = 'positive'
        elif emoji_str in negative_emojis: sentiment = 'negative'

        await self._append_activity_data(self.reaction_activity_file, {
            "user_id": payload.user_id, "sentiment": sentiment, "type": payload.event_type, "timestamp": datetime.now().isoformat()
        })

    async def track_member_join_leave(self, member: discord.Member, action: str):
        """Tracks when a member joins or leaves the server."""
        await self._append_activity_data(self.member_activity_file, {
            "user_id": member.id, "action": action, "timestamp": datetime.now().isoformat()
        })
        
    ############################################################################
    # DATA ANALYSIS & RETRIEVAL METHODS (Called by API endpoints)
    ############################################################################

    def get_channel_message_counts(self, days_back: int = 30) -> Dict[str, int]:
        """(PRESERVED FROM YOUR FILE) Reads the message log and maps channel_id to its message count."""
        counts = Counter()
        if not os.path.exists(self.message_activity_file): return counts
        cutoff = datetime.now() - timedelta(days=days_back)
        try:
            with open(self.message_activity_file, 'r', encoding='utf-8') as f:
                activities = json.load(f)
            for activity in activities:
                if datetime.fromisoformat(activity['timestamp']) >= cutoff:
                    counts[str(activity['channel_id'])] += 1
        except (IOError, json.JSONDecodeError): pass
        return dict(counts)

    def get_user_profile_activity(self, user_id: int, days_back: int = 365) -> Dict[str, Any]:
        """(PRESERVED FROM YOUR FILE) Generates a comprehensive activity profile for a single user."""
        summary = {"message_count_30d": 0, "top_channels": Counter(), "heatmap_data": Counter()}
        cutoff_30d = datetime.now() - timedelta(days=30)
        cutoff_year = datetime.now() - timedelta(days=days_back)
        if not os.path.exists(self.message_activity_file): return summary
        try:
            with open(self.message_activity_file, 'r', encoding='utf-8') as f:
                activities = json.load(f)
            user_messages = [a for a in activities if str(a.get("user_id")) == str(user_id)]
            for msg in user_messages:
                ts = datetime.fromisoformat(msg["timestamp"])
                if ts >= cutoff_year: summary["heatmap_data"][ts.strftime('%Y-%m-%d')] += 1
                if ts >= cutoff_30d:
                    summary["message_count_30d"] += 1
                    summary["top_channels"][str(msg.get("channel_id"))] += 1
        except (IOError, json.JSONDecodeError): pass
        return summary

    def get_user_activity_summary(self, user_id: int, hours_back: int = 24) -> Dict[str, Any]:
        """(PRESERVED FROM YOUR FILE) Gets a simple activity summary for a user over the last N hours."""
        summary = Counter()
        cutoff = datetime.now() - timedelta(hours=hours_back)
        # This function can be expanded to check voice/reaction files too if needed
        if os.path.exists(self.message_activity_file):
            try:
                with open(self.message_activity_file, 'r') as f:
                    activities = json.load(f)
                for act in activities:
                    if str(act.get('user_id')) == str(user_id) and datetime.fromisoformat(act['timestamp']) >= cutoff:
                        summary['messages'] += 1
            except (IOError, json.JSONDecodeError): pass
        return dict(summary)

    def get_user_activity_trends(self) -> Dict[str, Dict[str, Any]]:
        """Analyzes message activity to generate trends for all users (7d vs 30d)."""
        trends = {}
        if not os.path.exists(self.message_activity_file): return trends
        now, seven_days_ago, thirty_days_ago = datetime.now(), datetime.now() - timedelta(days=7), datetime.now() - timedelta(days=30)
        user_data = {}
        try:
            with open(self.message_activity_file, 'r', encoding='utf-8') as f:
                activities = json.load(f)

            for act in activities:
                try:
                    ts, uid = datetime.fromisoformat(act['timestamp']), str(act.get('user_id'))
                    if uid not in user_data:
                        user_data[uid] = {"recent_messages": 0, "baseline_messages": 0, "channels_recent": set(), "channels_baseline": set()}
                    if ts >= seven_days_ago:
                        user_data[uid]['recent_messages'] += 1
                        user_data[uid]['channels_recent'].add(str(act.get('channel_id')))
                    if ts >= thirty_days_ago:
                        user_data[uid]['baseline_messages'] += 1
                        user_data[uid]['channels_baseline'].add(str(act.get('channel_id')))
                except (ValueError, TypeError): continue
            
            for uid, data in user_data.items():
                avg_weekly_baseline = (data['baseline_messages'] / 30) * 7
                change = ((data['recent_messages'] - avg_weekly_baseline) / avg_weekly_baseline) * 100 if avg_weekly_baseline > 0 else 999 if data['recent_messages'] > 0 else 0
                trends[uid] = {
                    "messages_last_7d": data['recent_messages'], "avg_weekly_messages_30d": round(avg_weekly_baseline, 1),
                    "activity_change_percentage": round(change), "new_channels_visited": len(data["channels_recent"] - data["channels_baseline"])
                }
        except (json.JSONDecodeError, IOError): pass
        return trends

    def get_all_user_voice_time(self, days_back: int = 30) -> Counter:
        """Aggregates total voice chat minutes for all users."""
        totals = Counter()
        if not os.path.exists(self.voice_activity_file): return totals
        cutoff = datetime.now() - timedelta(days=days_back)
        try:
            with open(self.voice_activity_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            for log in logs:
                if datetime.fromisoformat(log['timestamp']) >= cutoff:
                    totals[str(log['user_id'])] += log['duration_minutes']
        except (IOError, json.JSONDecodeError): pass
        return totals
        
    def get_all_user_reaction_sentiments(self, days_back: int = 30) -> Dict[str, Counter]:
        """Aggregates positive vs. negative reactions given by all users."""
        sentiments = {}
        if not os.path.exists(self.reaction_activity_file): return sentiments
        cutoff = datetime.now() - timedelta(days=days_back)
        try:
            with open(self.reaction_activity_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            for log in logs:
                if datetime.fromisoformat(log['timestamp']) >= cutoff:
                    user_id = str(log['user_id'])
                    if user_id not in sentiments: sentiments[user_id] = Counter()
                    if log['type'] == 'REACTION_ADD':
                        sentiments[user_id][log['sentiment']] += 1
        except (IOError, json.JSONDecodeError): pass
        return sentiments

    def get_join_leave_history(self) -> Dict[str, List[Dict]]:
        """Returns a list of all join/leave events for each user."""
        history = {}
        if not os.path.exists(self.member_activity_file): return history
        try:
            with open(self.member_activity_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            for log in logs:
                user_id = str(log['user_id'])
                if user_id not in history: history[user_id] = []
                history[user_id].append({"action": log['action'], "timestamp": log['timestamp']})
        except (IOError, json.JSONDecodeError): pass
        return history

    def get_social_graph_stats(self, days_back: int = 30) -> Dict[str, Counter]:
        """Analyzes the social log to count incoming/outgoing interactions for each user."""
        stats = {}
        if not os.path.exists(self.social_activity_file): return stats
        cutoff = datetime.now() - timedelta(days=days_back)
        try:
            with open(self.social_activity_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)

            for log in logs:
                if datetime.fromisoformat(log['timestamp']) < cutoff: continue

                actor_id = str(log['actor_user_id'])
                if actor_id not in stats: stats[actor_id] = Counter()
                
                if log.get('replied_to_user_id'):
                    stats[actor_id]['replies_given'] += 1
                stats[actor_id]['mentions_given'] += len(log.get('mentioned_user_ids', []))

                if replied_to_id := log.get('replied_to_user_id'):
                    replied_to_id = str(replied_to_id)
                    if replied_to_id not in stats: stats[replied_to_id] = Counter()
                    stats[replied_to_id]['replies_received'] += 1
                
                for mentioned_id in log.get('mentioned_user_ids', []):
                    mentioned_id = str(mentioned_id)
                    if mentioned_id not in stats: stats[mentioned_id] = Counter()
                    stats[mentioned_id]['mentions_received'] += 1
        except (IOError, json.JSONDecodeError): pass
        return stats