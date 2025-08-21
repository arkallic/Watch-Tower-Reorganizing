# managers/moderation/case_manager.py
import os
import json
from datetime import datetime
from typing import Dict, List, Any

class CaseManager:
    def __init__(self, cases_dir: str, user_data: Dict[str, Any], logger, message_collector=None):
        self.cases_dir = cases_dir
        self.user_data = user_data
        self.logger = logger
        self.message_collector = message_collector  # Add this
    
    def get_next_case_number(self, user_id: int) -> int:
        """Get the next case number for a user"""
        user_key = str(user_id)
        if user_key not in self.user_data:
            self.user_data[user_key] = {"cases": []}
        
        existing_cases = self.user_data[user_key]["cases"]
        if not existing_cases:
            return 1
        
        return max(case.get("case_number", 0) for case in existing_cases) + 1
    
    async def create_case(self, user_id: int, action_data: Dict[str, Any], guild=None, bot=None) -> int:
        """Create a new moderation case with comprehensive data"""
        user_key = str(user_id)
        
        # Ensure user entry exists
        if user_key not in self.user_data:
            self.user_data[user_key] = {"cases": []}
        
        # Get case number
        case_number = self.get_next_case_number(user_id)
        
        # Get Discord user and moderator info
        user_avatar_url = None
        moderator_avatar_url = None
        user_context = {}
        guild_context = {}
        
        if guild and bot:
            try:
                # Get user info
                user = guild.get_member(user_id)
                if user:
                    user_avatar_url = str(user.display_avatar.url)
                    user_context = {
                        "account_age_days": (datetime.now() - user.created_at.replace(tzinfo=None)).days,
                        "server_join_days": (datetime.now() - user.joined_at.replace(tzinfo=None)).days if user.joined_at else 0,
                        "total_roles": len(user.roles),
                        "permissions": {
                            "administrator": user.guild_permissions.administrator,
                            "manage_messages": user.guild_permissions.manage_messages,
                            "kick_members": user.guild_permissions.kick_members,
                            "ban_members": user.guild_permissions.ban_members
                        }
                    }
                
                # Get moderator info
                moderator_id = action_data.get('moderator_id')
                if moderator_id:
                    moderator = guild.get_member(moderator_id)
                    if moderator:
                        moderator_avatar_url = str(moderator.display_avatar.url)
                
                # Guild context
                guild_context = {
                    "guild_id": guild.id,
                    "guild_name": guild.name
                }
                
            except Exception as e:
                self.logger.console_log_system(f"Error collecting user context: {e}", "WARNING")
        
        # Collect recent messages
        recent_messages = []
        if guild and self.message_collector:
            try:
                recent_messages = await self.message_collector.collect_user_messages(guild, user_id, 10)
            except Exception as e:
                self.logger.console_log_system(f"Error collecting recent messages: {e}", "WARNING")
        
        # Create comprehensive case data
        case_data = {
            "case_number": case_number,
            "user_id": user_id,
            "username": action_data.get('username', 'Unknown'),
            "display_name": action_data.get('display_name', 'Unknown'),
            "user_avatar_url": user_avatar_url,
            "moderator_id": action_data.get('moderator_id'),
            "moderator_name": action_data.get('moderator_name', 'Unknown'),
            "moderator_avatar_url": moderator_avatar_url,
            "action_type": action_data.get('action_type'),
            "timestamp": datetime.now().isoformat(),
            "created_at": datetime.now().isoformat(),
            "internal_comment": action_data.get('reason', ''),
            "user_comment": action_data.get('reason', ''),
            "reason": action_data.get('reason', ''),
            "dm_sent": action_data.get('dm_sent', False),
            "duration": action_data.get('duration'),
            "recent_messages": recent_messages,
            "flagged_message": action_data.get('flagged_message'),
            "modstring_triggered": action_data.get('modstring_triggered', False),
            "ai_confidence": action_data.get('ai_confidence'),
            "severity": action_data.get('severity', 'Low'),
            "resolvable": action_data.get('resolvable', 'Yes'),
            "status": "Open",
            "resolved_at": None,
            "resolved_by": None,
            "resolved_by_id": None,
            "resolution_method": None,
            "resolution_comment": "",
            "auto_resolve_at": None,
            "channel_context": {
                "total_channels_flagged": 0,  # You'll need to calculate this
                "most_active_channel": "unknown"  # You'll need to determine this
            },
            "user_context": user_context,
            "escalation_level": 0,
            "tags": action_data.get('tags', []),
            **guild_context
        }
        
        # Add to user data
        self.user_data[user_key]["cases"].append(case_data)
        
        # Save individual case file
        self._save_case_file(user_id, case_number, case_data)
        
        self.logger.console_log_system(f"Created case #{case_number} for user {user_id}")
        
        return case_number
    
    def get_user_cases(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all cases for a user"""
        user_key = str(user_id)
        return self.user_data.get(user_key, {}).get("cases", [])
    
    def get_case_by_number(self, user_id: int, case_number: int) -> Dict[str, Any]:
        """Get a specific case by number"""
        cases = self.get_user_cases(user_id)
        for case in cases:
            if case.get("case_number") == case_number:
                return case
        return {}
    
    def resolve_case(self, user_id: int, case_number: int, resolution: str, 
                    resolved_by: str) -> bool:
        """Resolve a case"""
        user_key = str(user_id)
        if user_key not in self.user_data:
            return False
        
        cases = self.user_data[user_key]["cases"]
        for case in cases:
            if case.get("case_number") == case_number and case.get("status") == "Open":
                case["status"] = "Resolved"
                case["resolution"] = resolution
                case["resolved_by"] = resolved_by
                case["resolved_at"] = datetime.now().isoformat()
                
                # Update case file
                self._save_case_file(user_id, case_number, case)
                
                self.logger.console_log_system(
                    f"Resolved case #{case_number} for user {user_id}",
                    "CASE"
                )
                return True
        
        return False
    
    def _save_case_file(self, user_id: int, case_number: int, case_data: Dict[str, Any]):
        """Save individual case file"""
        try:
            filename = f"case_{user_id}_{case_number}.json"
            filepath = os.path.join(self.cases_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(case_data, f, indent=2, ensure_ascii=False, default=str)
                
        except Exception as e:
            self.logger.console_log_system(f"Error saving case file: {e}", "ERROR")
    
    def get_open_cases_count(self) -> int:
        """Get total number of open cases across all users"""
        total = 0
        for user_data in self.user_data.values():
            cases = user_data.get("cases", [])
            total += len([c for c in cases if c.get("status") == "Open"])
        return total
    
    def get_cases_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get all cases within a date range"""
        all_cases = []
        
        for user_id, user_data in self.user_data.items():
            cases = user_data.get("cases", [])
            for case in cases:
                try:
                    case_date = datetime.fromisoformat(case.get("timestamp", ""))
                    if start_date <= case_date <= end_date:
                        case_copy = case.copy()
                        case_copy["user_id"] = user_id
                        all_cases.append(case_copy)
                except (ValueError, TypeError):
                    continue
        
        return sorted(all_cases, key=lambda x: x.get("timestamp", ""), reverse=True)