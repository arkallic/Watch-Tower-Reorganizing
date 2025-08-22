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
        self.script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = os.path.join(self.script_dir, "data")
        self.flagged_file = os.path.join(self.data_dir, "flagged_messages.json")
        self.ensure_directories()
        self.flagged_data = self.load_flagged_data()
    
    def ensure_directories(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def load_flagged_data(self) -> List[Dict[str, Any]]:
        try:
            if os.path.exists(self.flagged_file):
                with open(self.flagged_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"{Fore.RED}❌ Error loading flagged data: {e}{Style.RESET_ALL}")
            return []
    
    def save_flagged_data(self) -> bool:
        try:
            with open(self.flagged_file, 'w', encoding='utf-8') as f:
                json.dump(self.flagged_data, f, indent=2, ensure_ascii=False, default=str)
            return True
        except Exception as e:
            print(f"{Fore.RED}❌ Error saving flagged data: {e}{Style.RESET_ALL}")
            return False

    def console_log_system(self, message: str, level: str = "INFO"):
        """A centralized method for logging system messages to the console."""
        color_map = {
            "INFO": Fore.CYAN, "SUCCESS": Fore.GREEN, "WARNING": Fore.YELLOW,
            "ERROR": Fore.RED, "ACTION": Fore.MAGENTA, "CASE": Fore.BLUE,
        }
        color = color_map.get(level.upper(), Fore.WHITE)
        print(f"{color}[{level.upper()}] {message}{Style.RESET_ALL}")

    def get_all_flags(self, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        try:
            if user_id is not None:
                return [f for f in self.flagged_data if str(f.get("user_id")) == str(user_id)]
            return self.flagged_data
        except Exception as e:
            print(f"{Fore.RED}❌ Error in get_all_flags: {e}{Style.RESET_ALL}")
            return []

    def log_flagged_message(self, user_id: int, username: str, display_name: str, 
                           content: str, timestamp: datetime, message_url: str,
                           **kwargs):
        try:
            flag_entry = {
                "user_id": user_id, "username": username, "display_name": display_name,
                "content": content, "timestamp": timestamp.isoformat(), "message_url": message_url,
                "confidence": kwargs.get("confidence", 0), "flags": kwargs.get("flags", {}),
                "ai_explanation": kwargs.get("ai_explanation", ""), "channel_id": kwargs.get("channel_id"),
                "channel_name": kwargs.get("channel_name", "Unknown"),
                "logged_at": datetime.now().isoformat(), "reviewed": False,
            }
            self.flagged_data.append(flag_entry)
            self.save_flagged_data()
            return True
        except Exception as e:
            self.console_log_system(f"Error logging flagged message: {e}", "ERROR")
            return False