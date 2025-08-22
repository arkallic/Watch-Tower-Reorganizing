# managers/moderation/case_manager.py
import os
import json
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

class CaseManager:
    def __init__(self, cases_dir: str, logger, message_collector=None, deleted_message_logger=None):
        self.cases_dir = cases_dir
        self.logger = logger
        self.message_collector = message_collector
        self.deleted_message_logger = deleted_message_logger
    
    def get_next_case_number(self) -> int:
        """Get the next global case number by scanning the case files."""
        cases_path = Path(self.cases_dir)
        if not cases_path.exists() or not any(cases_path.glob("case_*.json")):
            return 1
        
        max_case_num = 0
        for f in cases_path.glob("case_*.json"):
            try:
                case_num = int(f.stem.split('_')[-1])
                if case_num > max_case_num:
                    max_case_num = case_num
            except (ValueError, IndexError):
                continue
        return max_case_num + 1

    async def create_case(self, user_id: int, action_data: Dict[str, Any], guild=None, bot=None) -> int:
        """Create a new moderation case and save it as an individual file."""
        case_number = self.get_next_case_number()
        
        user_avatar_url, moderator_avatar_url, user_context, guild_context = None, None, {}, {}
        
        if guild and bot:
            try:
                if user := guild.get_member(user_id):
                    user_avatar_url = str(user.display_avatar.url)
                    user_context = {"account_age_days": (datetime.now() - user.created_at.replace(tzinfo=None)).days}
                if mod_id := action_data.get('moderator_id'):
                    if moderator := guild.get_member(mod_id):
                        moderator_avatar_url = str(moderator.display_avatar.url)
                guild_context = {"guild_id": guild.id, "guild_name": guild.name}
            except Exception as e:
                self.logger.console_log_system(f"Error collecting user context: {e}", "WARNING")
        
        recent_messages = []
        if guild and self.message_collector:
            recent_messages = await self.message_collector.collect_user_messages(guild, user_id, 10)
        
        # --- NEW FEATURE: INCLUDE RECENTLY DELETED MESSAGES ---
        recent_deletions = []
        if self.deleted_message_logger:
            recent_deletions = self.deleted_message_logger.get_user_deleted_messages(user_id, hours=24)
        # --- END OF NEW FEATURE ---

        channel_obj = action_data.get('channel')
        channel_id = channel_obj.id if channel_obj else None
        channel_name = channel_obj.name if channel_obj else "Unknown"

        case_data = {
            "case_number": case_number, "user_id": user_id,
            "username": action_data.get('username', 'Unknown'),
            "display_name": action_data.get('display_name', 'Unknown'),
            "user_avatar_url": user_avatar_url,
            "moderator_id": action_data.get('moderator_id'),
            "moderator_name": action_data.get('moderator_name', 'Unknown'),
            "moderator_avatar_url": moderator_avatar_url,
            "action_type": action_data.get('action_type'),
            "channel_id": channel_id, "channel_name": channel_name,
            "timestamp": datetime.now().isoformat(), "created_at": datetime.now().isoformat(),
            "reason": action_data.get('reason', ''),
            "dm_sent": action_data.get('dm_sent', False), "duration": action_data.get('duration'),
            "recent_messages": recent_messages,
            "recent_deletions": recent_deletions[:5], # Include up to 5 recent deletions
            "severity": action_data.get('severity', 'Low'),
            "status": "Open", "resolved_at": None, "resolved_by": None,
            "user_context": user_context, "tags": action_data.get('tags', []),
            **guild_context
        }
        
        self._save_case_file(user_id, case_number, case_data)
        self.logger.console_log_system(f"Created case #{case_number} for user {user_id} in #{channel_name}", "CASE")
        
        return case_number
    
    def _save_case_file(self, user_id: int, case_number: int, case_data: Dict[str, Any]) -> bool:
        """Save an individual case file."""
        try:
            filename = f"case_{user_id}_{case_number}.json"
            filepath = os.path.join(self.cases_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(case_data, f, indent=2, ensure_ascii=False, default=str)
            return True
        except Exception as e:
            self.logger.console_log_system(f"Error saving case file: {e}", "ERROR")
            return False