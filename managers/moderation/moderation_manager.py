# managers/moderation/moderation_manager.py
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
from colorama import Fore, Style
from core.settings import bot_settings

from .validation_manager import ValidationManager
from .case_manager import CaseManager
from .message_collector import MessageCollector
from .action_executor import ActionExecutor
from .statistics_manager import StatisticsManager

class ModerationManager:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.settings = bot_settings
        
        # Setup directories and data - point to root level
        self.script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.cases_dir = os.path.join(self.script_dir, "cases")
        self.user_data_file = os.path.join(self.cases_dir, "user_moderation_data.json")
        self.ensure_directories()
        self.user_data = self.load_user_data()
        
        # Initialize sub-managers
        self.validator = ValidationManager(self.settings)
        self.message_collector = MessageCollector(logger)
        self.case_manager = CaseManager(self.cases_dir, self.user_data, logger, self.message_collector)
        self.action_executor = ActionExecutor(logger)
        self.statistics_manager = StatisticsManager(self.user_data)
    
    def ensure_directories(self):
        """Ensure cases directory exists"""
        if not os.path.exists(self.cases_dir):
            os.makedirs(self.cases_dir)
    
    def load_user_data(self) -> Dict[str, Any]:
        """Load user moderation data"""
        try:
            if os.path.exists(self.user_data_file):
                with open(self.user_data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"{Fore.RED}❌ Error loading user data: {e}{Style.RESET_ALL}")
            return {}
    
    def save_user_data(self) -> bool:
        """Save user moderation data"""
        try:
            with open(self.user_data_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_data, f, indent=2, ensure_ascii=False, default=str)
            return True
        except Exception as e:
            print(f"{Fore.RED}❌ Error saving user data: {e}{Style.RESET_ALL}")
            return False
    
    # Delegate methods to sub-managers
    def user_can_moderate(self, user_roles: List[int]) -> bool:
        return self.validator.user_can_moderate(user_roles)
    
    def user_is_admin(self, user_roles: List[int]) -> bool:
        return self.validator.user_is_admin(user_roles)
    
    def get_next_case_number(self, user_id: int) -> int:
        return self.case_manager.get_next_case_number(user_id)
    
    async def collect_user_messages(self, guild, user_id: int, limit: int = 10):
        return await self.message_collector.collect_user_messages(guild, user_id, limit)
    
    def get_moderation_summary(self, days: int = 30):
        self.statistics_manager.user_data = self.user_data
        return self.statistics_manager.get_moderation_summary(days)
    
    def export_cases_to_csv(self, output_file: str = None):
        self.statistics_manager.user_data = self.user_data
        return self.statistics_manager.export_cases_to_csv(output_file)
    
    # Main coordination methods
    async def create_moderation_case(self, user_id: int, action_data: Dict[str, Any], guild=None, bot=None) -> int:
        """Create a new moderation case with all related actions"""
        # Validation
        if not self.validator.validate_action_type(action_data.get("action_type", "")):
            raise ValueError("Invalid action type")
        
        if not self.validator.validate_severity(action_data.get("severity", "")):
            raise ValueError("Invalid severity")
        
        # Create case with rich data (now async)
        case_number = await self.case_manager.create_case(user_id, action_data, guild, bot)
        
        # Update user stats
        self._update_user_stats(str(user_id))
        
        # Save data
        self.save_user_data()
        
        return case_number
    
    def _update_user_stats(self, user_key: str):
        """Update summary statistics for a user"""
        cases = self.user_data[user_key]["cases"]
        
        # Calculate stats
        total_cases = len(cases)
        open_cases = len([c for c in cases if c.get("status") == "Open"])
        warns = len([c for c in cases if c.get("action_type") == "warn"])
        timeouts = len([c for c in cases if c.get("action_type") == "timeout"])
        kicks = len([c for c in cases if c.get("action_type") == "kick"])
        bans = len([c for c in cases if c.get("action_type") == "ban"])
        
        # Store stats
        self.user_data[user_key].update({
            "total_cases": total_cases,
            "open_cases": open_cases,
            "warns": warns,
            "timeouts": timeouts,
            "kicks": kicks,
            "bans": bans,
            "last_case_date": cases[-1]["timestamp"] if cases else None,
            "escalation_level": len([c for c in cases if c.get("severity") in ["High", "Critical"]])
        })

    # API compatibility methods
    def get_case_file_path(self, user_id: int, case_number: int) -> str:
        """Get the file path for a specific case"""
        filename = f"case_{user_id}_{case_number}.json"
        return os.path.join(self.cases_dir, filename)
    
    def get_all_cases(self) -> List[Dict[str, Any]]:
        """Get all cases across all users"""
        all_cases = []
        for user_id, user_data in self.user_data.items():
            cases = user_data.get("cases", [])
            for case in cases:
                case_copy = case.copy()
                case_copy["user_id"] = int(user_id)
                all_cases.append(case_copy)
        
        # Sort by case creation date (newest first)
        return sorted(all_cases, key=lambda x: x.get("timestamp", ""), reverse=True)
    
    def resolve_case(self, user_id: int, case_number: int, resolver_id: int, 
                    method: str, comment: str, status: str = "Resolved") -> bool:
        """Resolve a case with the new method signature"""
        return self.case_manager.resolve_case(user_id, case_number, comment, f"User {resolver_id}")
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Get user statistics - delegate to statistics manager"""
        self.statistics_manager.user_data = self.user_data
        return self.statistics_manager.get_user_stats(user_id)
    
    def get_user_case_by_number(self, user_id: int, case_number: int) -> Dict[str, Any]:
        """Get specific case by user ID and case number"""
        return self.case_manager.get_case_by_number(user_id, case_number)
    
    def update_case(self, user_id: int, case_number: int, updates: Dict[str, Any]) -> bool:
        """Update a case with new data"""
        user_key = str(user_id)
        if user_key not in self.user_data:
            return False
        
        cases = self.user_data[user_key]["cases"]
        for case in cases:
            if case.get("case_number") == case_number:
                case.update(updates)
                case["last_modified"] = datetime.now().isoformat()
                
                # Update case file
                self.case_manager._save_case_file(user_id, case_number, case)
                
                # Save user data
                self.save_user_data()
                return True
        
        return False
    
    def delete_case(self, user_id: int, case_number: int) -> bool:
        """Delete a case"""
        user_key = str(user_id)
        if user_key not in self.user_data:
            return False
        
        cases = self.user_data[user_key]["cases"]
        for i, case in enumerate(cases):
            if case.get("case_number") == case_number:
                # Remove from user data
                del cases[i]
                
                # Delete case file
                try:
                    case_file = self.get_case_file_path(user_id, case_number)
                    if os.path.exists(case_file):
                        os.remove(case_file)
                except:
                    pass
                
                # Update user stats
                self._update_user_stats(user_key)
                
                # Save user data
                self.save_user_data()
                return True
        
        return False