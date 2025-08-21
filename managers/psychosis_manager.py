# managers/psychosis_manager.py
import discord
from discord.ext import commands
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import json
import os
from colorama import Fore, Style

from .psychosis.restriction_manager import RestrictionManager
from .psychosis.notification_manager import NotificationManager
from .psychosis.timer_manager import TimerManager

class PsychosisManager:
    def __init__(self, config_manager, logger):
        self.config = config_manager
        self.logger = logger
        self.active_restrictions = {}
        
        # Get the directory where this script is located
        self.script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Go up two levels
        self.data_dir = os.path.join(self.script_dir, "data")
        self.restrictions_file = os.path.join(self.data_dir, "psychosis_restrictions.json")
        self.ensure_directories()
        self.load_active_restrictions()
        
        # Initialize sub-managers
        self.restriction_manager = RestrictionManager(config_manager, logger)
        self.notification_manager = NotificationManager(config_manager, logger)
        self.timer_manager = TimerManager(self)
    
    def ensure_directories(self):
        """Ensure necessary directories exist"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def load_active_restrictions(self):
        """Load active restrictions from file"""
        if os.path.exists(self.restrictions_file):
            try:
                with open(self.restrictions_file, 'r', encoding='utf-8') as f:
                    self.active_restrictions = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.active_restrictions = {}
    
    def save_active_restrictions(self):
        """Save active restrictions to file"""
        try:
            with open(self.restrictions_file, 'w', encoding='utf-8') as f:
                json.dump(self.active_restrictions, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"{Fore.RED}❌ Error saving restrictions: {e}{Style.RESET_ALL}")
    
    def get_user_restriction(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get active restriction for a user"""
        return self.active_restrictions.get(str(user_id))
    
    def add_user_restriction(self, user_id: int, restriction_data: Dict[str, Any]):
        """Add a new user restriction"""
        user_key = str(user_id)
        self.active_restrictions[user_key] = restriction_data
        self.save_active_restrictions()
    
    def remove_user_restriction(self, user_id: int) -> bool:
        """Remove a user restriction"""
        user_key = str(user_id)
        if user_key in self.active_restrictions:
            del self.active_restrictions[user_key]
            self.save_active_restrictions()
            return True
        return False
    
    async def apply_restriction(self, bot, guild: discord.Guild, user: discord.Member, 
                              restriction_type: str, duration_minutes: int, 
                              moderator: discord.Member, user_comment: str = "", 
                              mod_comment: str = "") -> bool:
        """Apply a psychosis restriction to a user"""
        try:
            # Apply the actual Discord permissions
            success = await self.restriction_manager.apply_restriction(
                guild, user, restriction_type
            )
            
            if not success:
                return False
            
            # Create restriction record
            restriction_data = {
                "type": restriction_type,
                "started_at": datetime.now().isoformat(),
                "duration_minutes": duration_minutes,
                "moderator_id": moderator.id,
                "moderator_name": moderator.display_name,
                "user_comment": user_comment,
                "mod_comment": mod_comment,
                "guild_id": guild.id
            }
            
            self.add_user_restriction(user.id, restriction_data)
            
            # Start auto-removal timer
            await self.timer_manager.start_restriction_timer(
                bot, user.id, restriction_type, duration_minutes
            )
            
            # Send notifications
            await self.notification_manager.send_restriction_notifications(
                bot, guild, user, restriction_type, restriction_data
            )
            
            self.logger.console_log_system(
                f"Applied {restriction_type} restriction to {user.display_name} for {duration_minutes} minutes",
                "PSYCHOSIS"
            )
            
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error applying restriction: {e}{Style.RESET_ALL}")
            return False
    
    async def remove_restriction(self, bot, user_id: int, reason: str = "Manual removal") -> bool:
        """Remove a psychosis restriction from a user"""
        try:
            restriction_data = self.get_user_restriction(user_id)
            if not restriction_data:
                return False
            
            guild = bot.get_guild(restriction_data.get("guild_id"))
            if not guild:
                return False
            
            user = guild.get_member(user_id)
            if not user:
                return False
            
            # Remove Discord permissions
            await self.restriction_manager.remove_restriction(
                guild, user, restriction_data.get("type", "unknown")
            )
            
            # Remove from active restrictions
            self.remove_user_restriction(user_id)
            
            # Send end notifications
            await self.notification_manager.send_restriction_ended_notification(
                bot, guild, user, restriction_data, reason
            )
            
            self.logger.console_log_system(
                f"Removed restriction from {user.display_name}: {reason}",
                "PSYCHOSIS"
            )
            
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error removing restriction: {e}{Style.RESET_ALL}")
            return False
    
    def get_restriction_stats(self) -> Dict[str, Any]:
        """Get statistics about active restrictions"""
        total_restrictions = len(self.active_restrictions)
        
        restriction_types = {}
        for restriction in self.active_restrictions.values():
            r_type = restriction.get("type", "Unknown")
            restriction_types[r_type] = restriction_types.get(r_type, 0) + 1
        
        return {
            "total_active": total_restrictions,
            "by_type": restriction_types,
            "oldest_restriction": min(
                (r.get("started_at") for r in self.active_restrictions.values()),
                default=None
            )
        }