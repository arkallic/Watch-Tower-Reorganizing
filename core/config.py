# core/config.py
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from colorama import Fore, Style

class ConfigManager:
    def __init__(self):
        # Point to root directory
        self.script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Go up two levels
        self.config_file = os.path.join(self.script_dir, "config.json")
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return self.get_default_config()
        except Exception as e:
            print(f"{Fore.RED}❌ Error loading config: {e}{Style.RESET_ALL}")
            return self.get_default_config()
    
    def save_config(self) -> bool:
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"{Fore.RED}❌ Error saving config: {e}{Style.RESET_ALL}")
            return False
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "version": "2.0.0",
            "debug": False,
            "log_level": "INFO",
            "api_port": 8001,
            "dashboard_port": 3000,
            "forge_studio_port": 8000,
            "max_message_age_days": 7,
            "auto_backup_enabled": True,
            "auto_backup_interval_hours": 24,
            "features": {
                "ai_moderation": True,
                "modstring_evaluation": True,
                "psychosis_management": True,
                "activity_tracking": True,
                "report_generation": True
            },
            "performance": {
                "message_cache_size": 1000,
                "api_rate_limit": 100,
                "concurrent_evaluations": 5
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> bool:
        """Set configuration value"""
        keys = key.split('.')
        config = self.config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
        return self.save_config()
    
    def update(self, updates: Dict[str, Any]) -> bool:
        """Update multiple configuration values"""
        self.config.update(updates)
        return self.save_config()
    
    def reload(self) -> bool:
        """Reload configuration from file"""
        try:
            self.config = self.load_config()
            return True
        except Exception as e:
            print(f"{Fore.RED}❌ Error reloading config: {e}{Style.RESET_ALL}")
            return False