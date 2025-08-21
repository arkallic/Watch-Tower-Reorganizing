# utils/data_persistence.py
import json
import os
from typing import Dict, Any, List
from colorama import Fore, Style

class DataPersistence:
    def __init__(self):
        # Point to root directory
        self.script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Go up two levels
        self.data_dir = os.path.join(self.script_dir, "persistent_data")
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.modstrings_file = os.path.join(self.data_dir, "active_modstrings.json")
        self.lists_file = os.path.join(self.data_dir, "word_lists.json")
        self.state_file = os.path.join(self.data_dir, "modstring_state.json")
        
    async def save_modstrings(self, modstrings: Dict[str, Any]):
        """Save active modstrings to disk"""
        try:
            with open(self.modstrings_file, 'w', encoding='utf-8') as f:
                json.dump(modstrings, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"{Fore.RED}❌ Error saving modstrings: {e}{Style.RESET_ALL}")
            return False
    
    async def load_modstrings(self) -> Dict[str, Any]:
        """Load active modstrings from disk"""
        try:
            if os.path.exists(self.modstrings_file):
                with open(self.modstrings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"{Fore.RED}❌ Error loading modstrings: {e}{Style.RESET_ALL}")
            return {}
    
    async def save_word_lists(self, word_lists: Dict[str, Any]):
        """Save word lists to disk"""
        try:
            with open(self.lists_file, 'w', encoding='utf-8') as f:
                json.dump(word_lists, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"{Fore.RED}❌ Error saving word lists: {e}{Style.RESET_ALL}")
            return False
    
    async def load_word_lists(self) -> Dict[str, Any]:
        """Load word lists from disk"""
        try:
            if os.path.exists(self.lists_file):
                with open(self.lists_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"{Fore.RED}❌ Error loading word lists: {e}{Style.RESET_ALL}")
            return {}
    
    async def save_state(self, state: Dict[str, Any]):
        """Save general state data"""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"{Fore.RED}❌ Error saving state: {e}{Style.RESET_ALL}")
            return False
    
    async def load_state(self) -> Dict[str, Any]:
        """Load general state data"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"{Fore.RED}❌ Error loading state: {e}{Style.RESET_ALL}")
            return {}