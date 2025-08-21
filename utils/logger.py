# utils/logger.py
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from colorama import Fore, Style
from core.settings import bot_settings

class Logger:
    def __init__(self):
        self.settings = bot_settings
        # Update path to point to root directory
        self.script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Go up two levels
        self.data_dir = os.path.join(self.script_dir, "data")
        self.flagged_file = os.path.join(self.data_dir, "flagged_messages.json")
        self.ensure_directories()
        self.flagged_data = self.load_flagged_data()
    
    def ensure_directories(self):
        """Ensure data directory exists"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def load_flagged_data(self) -> List[Dict[str, Any]]:
        """Load flagged messages data"""
        try:
            if os.path.exists(self.flagged_file):
                with open(self.flagged_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"{Fore.RED}❌ Error loading flagged data: {e}{Style.RESET_ALL}")
            return []
    
    def save_flagged_data(self) -> bool:
        """Save flagged messages data"""
        try:
            with open(self.flagged_file, 'w', encoding='utf-8') as f:
                json.dump(self.flagged_data, f, indent=2, ensure_ascii=False, default=str)
            return True
        except Exception as e:
            print(f"{Fore.RED}❌ Error saving flagged data: {e}{Style.RESET_ALL}")
            return False
    
    def should_flag_message(self, confidence_score: float, flags: Dict[str, Any] = None) -> bool:
        """Check if message should be flagged based on threshold and flags"""
        threshold = self.settings.get("flag_threshold", 7)
        
        # Convert 1-10 scale to percentage (threshold * 10)
        threshold_percentage = threshold * 10
        
        # Check confidence score
        if confidence_score >= threshold_percentage:
            return True
        
        # Check for specific high-priority flags
        if flags:
            high_priority_flags = ["harassment", "threats", "hate_speech", "explicit_content"]
            for flag_type in high_priority_flags:
                if flags.get(flag_type, False):
                    return True
        
        return False
    
    def log_flagged_message(self, user_id: int, username: str, display_name: str, 
                           content: str, timestamp: datetime, message_url: str,
                           confidence: float = 0, flags: Dict[str, Any] = None,
                           ai_explanation: str = "", channel_id: int = None,
                           channel_name: str = "Unknown", modstring_triggered: bool = False) -> bool:
        """Log a flagged message with enhanced metadata"""
        try:
            flag_entry = {
                "user_id": user_id,
                "username": username,
                "display_name": display_name,
                "content": content,
                "timestamp": timestamp.isoformat() if isinstance(timestamp, datetime) else timestamp,
                "message_url": message_url,
                "confidence": confidence,
                "flags": flags or {},
                "ai_explanation": ai_explanation,
                "channel_id": channel_id,
                "channel_name": channel_name,
                "modstring_triggered": modstring_triggered,
                "flag_threshold_used": self.settings.get("flag_threshold", 7),
                "logged_at": datetime.now().isoformat(),
                "processed": False,
                "reviewed": False,
                "reviewer_id": None,
                "review_notes": "",
                "escalated": False
            }
            
            self.flagged_data.append(flag_entry)
            
            # Auto-cleanup old entries (older than max_case_age_days)
            max_age_days = self.settings.get("max_case_age_days", 365)
            cutoff_date = datetime.now() - timedelta(days=max_age_days)
            
            self.flagged_data = [
                entry for entry in self.flagged_data
                if datetime.fromisoformat(entry["timestamp"].replace('Z', '+00:00')).replace(tzinfo=None) > cutoff_date
            ]
            
            success = self.save_flagged_data()
            
            if success and self.settings.get("debug_mode", False):
                print(f"{Fore.CYAN}📝 Logged flagged message from {username} (confidence: {confidence}%){Style.RESET_ALL}")
            
            return success
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error logging flagged message: {e}{Style.RESET_ALL}")
            return False
    
    def get_user_flags(self, user_id: int, hours_back: int = 24) -> Dict[str, Any]:
        """Get user's flagged messages within time window"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            
            user_flags = [
                entry for entry in self.flagged_data
                if entry["user_id"] == user_id and
                datetime.fromisoformat(entry["timestamp"].replace('Z', '+00:00')).replace(tzinfo=None) > cutoff_time
            ]
            
            total_flags = len([entry for entry in self.flagged_data if entry["user_id"] == user_id])
            recent_flags = len(user_flags)
            
            # Calculate average confidence
            avg_confidence = 0
            if user_flags:
                avg_confidence = sum(flag.get("confidence", 0) for flag in user_flags) / len(user_flags)
            
            # Get flag types breakdown
            flag_types = {}
            for flag in user_flags:
                for flag_type, active in flag.get("flags", {}).items():
                    if active:
                        flag_types[flag_type] = flag_types.get(flag_type, 0) + 1
            
            return {
                "total_flags": total_flags,
                "recent_flags": recent_flags,
                "avg_confidence": round(avg_confidence, 1),
                "flag_types": flag_types,
                "latest_flags": sorted(user_flags, key=lambda x: x["timestamp"], reverse=True)[:5],
                "escalation_needed": recent_flags >= self.settings.get("messages_per_case", 10)
            }
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error getting user flags: {e}{Style.RESET_ALL}")
            return {
                "total_flags": 0,
                "recent_flags": 0,
                "avg_confidence": 0,
                "flag_types": {},
                "latest_flags": [],
                "escalation_needed": False
            }
    
    def get_global_stats(self, hours_back: int = 168) -> Dict[str, Any]:
        """Get global flagging statistics"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            
            recent_flags = [
                entry for entry in self.flagged_data
                if datetime.fromisoformat(entry["timestamp"].replace('Z', '+00:00')).replace(tzinfo=None) > cutoff_time
            ]
            
            # Basic stats
            total_flags = len(self.flagged_data)
            recent_count = len(recent_flags)
            
            # Unique users flagged
            unique_users = len(set(entry["user_id"] for entry in recent_flags))
            
            # Average confidence
            avg_confidence = 0
            if recent_flags:
                avg_confidence = sum(flag.get("confidence", 0) for flag in recent_flags) / len(recent_flags)
            
            # Top flagged users
            user_counts = {}
            for flag in recent_flags:
                user_id = flag["user_id"]
                user_counts[user_id] = user_counts.get(user_id, 0) + 1
            
            top_users = sorted(user_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Flag types breakdown
            flag_types = {}
            for flag in recent_flags:
                for flag_type, active in flag.get("flags", {}).items():
                    if active:
                        flag_types[flag_type] = flag_types.get(flag_type, 0) + 1
            
            # Channel breakdown
            channel_stats = {}
            for flag in recent_flags:
                channel = flag.get("channel_name", "Unknown")
                channel_stats[channel] = channel_stats.get(channel, 0) + 1
            
            # Hourly breakdown for recent flags
            hourly_stats = {}
            for flag in recent_flags:
                hour = datetime.fromisoformat(flag["timestamp"].replace('Z', '+00:00')).replace(tzinfo=None).hour
                hourly_stats[hour] = hourly_stats.get(hour, 0) + 1
            
            return {
                "total_flags": total_flags,
                "recent_flags": recent_count,
                "unique_users_flagged": unique_users,
                "avg_confidence": round(avg_confidence, 1),
                "top_flagged_users": top_users,
                "flag_types_breakdown": flag_types,
                "channel_breakdown": channel_stats,
                "hourly_breakdown": hourly_stats,
                "escalation_rate": len([f for f in recent_flags if f.get("escalated", False)]) / recent_count * 100 if recent_count > 0 else 0
            }
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error getting global stats: {e}{Style.RESET_ALL}")
            return {
                "total_flags": 0,
                "recent_flags": 0,
                "unique_users_flagged": 0,
                "avg_confidence": 0,
                "top_flagged_users": [],
                "flag_types_breakdown": {},
                "channel_breakdown": {},
                "hourly_breakdown": {},
                "escalation_rate": 0
            }
    
    def mark_flag_reviewed(self, flag_index: int, reviewer_id: int, notes: str = "") -> bool:
        """Mark a flagged message as reviewed"""
        try:
            if 0 <= flag_index < len(self.flagged_data):
                self.flagged_data[flag_index].update({
                    "reviewed": True,
                    "reviewer_id": reviewer_id,
                    "review_notes": notes,
                    "reviewed_at": datetime.now().isoformat()
                })
                return self.save_flagged_data()
            return False
        except Exception as e:
            print(f"{Fore.RED}❌ Error marking flag as reviewed: {e}{Style.RESET_ALL}")
            return False
    
    def escalate_flag(self, flag_index: int, escalator_id: int, reason: str = "") -> bool:
        """Escalate a flagged message"""
        try:
            if 0 <= flag_index < len(self.flagged_data):
                self.flagged_data[flag_index].update({
                    "escalated": True,
                    "escalator_id": escalator_id,
                    "escalation_reason": reason,
                    "escalated_at": datetime.now().isoformat()
                })
                return self.save_flagged_data()
            return False
        except Exception as e:
            print(f"{Fore.RED}❌ Error escalating flag: {e}{Style.RESET_ALL}")
            return False
    
    def get_report_channel_id(self) -> Optional[int]:
        """Get the configured report channel"""
        channel_id = self.settings.get("report_channel")
        return int(channel_id) if channel_id else None
    
    def cleanup_old_flags(self) -> int:
        """Clean up old flagged messages based on settings"""
        try:
            max_age_days = self.settings.get("max_case_age_days", 365)
            cutoff_date = datetime.now() - timedelta(days=max_age_days)
            
            original_count = len(self.flagged_data)
            
            self.flagged_data = [
                entry for entry in self.flagged_data
                if datetime.fromisoformat(entry["timestamp"].replace('Z', '+00:00')).replace(tzinfo=None) > cutoff_date
            ]
            
            cleaned_count = original_count - len(self.flagged_data)
            
            if cleaned_count > 0:
                self.save_flagged_data()
                print(f"{Fore.CYAN}🧹 Cleaned up {cleaned_count} old flagged messages{Style.RESET_ALL}")
            
            return cleaned_count
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error cleaning up old flags: {e}{Style.RESET_ALL}")
            return 0