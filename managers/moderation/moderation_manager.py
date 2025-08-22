# managers/moderation/moderation_manager.py
import json
import os
from typing import Dict, List, Any
from pathlib import Path
from colorama import Fore, Style
from core.settings import bot_settings

from .validation_manager import ValidationManager
from .case_manager import CaseManager
from .message_collector import MessageCollector
from .action_executor import ActionExecutor

class ModerationManager:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.settings = bot_settings
        
        self.script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.cases_dir = os.path.join(self.script_dir, "cases")
        self.ensure_directories()
        
        self.validator = ValidationManager(self.settings)
        self.message_collector = MessageCollector(logger)
        self.case_manager = CaseManager(self.cases_dir, logger, self.message_collector)
        self.action_executor = ActionExecutor(logger)

    def ensure_directories(self):
        if not os.path.exists(self.cases_dir):
            os.makedirs(self.cases_dir)

    def get_all_cases(self) -> List[Dict[str, Any]]:
        """
        Get all cases by reading directly from the individual case files.
        This is now the single, authoritative source of truth for case data.
        """
        all_cases = []
        cases_path = Path(self.cases_dir)
        if not cases_path.exists():
            return []

        for case_file in cases_path.glob("case_*.json"):
            try:
                with open(case_file, 'r', encoding='utf-8') as f:
                    all_cases.append(json.load(f))
            except Exception as e:
                self.logger.console_log_system(f"Error loading case file {case_file.name}: {e}", "ERROR")
                continue
        
        all_cases.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return all_cases

    async def create_moderation_case(self, user_id: int, action_data: Dict[str, Any], guild=None, bot=None) -> int:
        """Validates and creates a new moderation case via the CaseManager."""
        if not self.validator.validate_action_type(action_data.get("action_type", "")):
            raise ValueError("Invalid action type")
        
        # The CaseManager now handles all file operations.
        return await self.case_manager.create_case(user_id, action_data, guild, bot)

    def get_user_case_by_number(self, user_id: int, case_number: int) -> Dict[str, Any]:
        """Finds a specific case by iterating through all case files."""
        for case in self.get_all_cases():
            if str(case.get("user_id")) == str(user_id) and case.get("case_number") == case_number:
                return case
        return {}

    def update_case(self, user_id: int, case_number: int, updates: Dict[str, Any]) -> bool:
        """Updates and saves an individual case file."""
        case = self.get_user_case_by_number(user_id, case_number)
        if not case:
            return False
        
        case.update(updates)
        return self.case_manager._save_case_file(user_id, case_number, case)