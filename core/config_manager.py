# core/config_manager.py
from core.settings import bot_settings

class ConfigManager:
    """Wrapper for bot settings with additional config functionality"""
    
    def __init__(self):
        self.settings = bot_settings
    
    def get(self, key: str, default=None):
        """Get a configuration value"""
        return self.settings.get(key, default)
    
    def update(self, updates: dict, updated_by: str = "system") -> bool:
        """Update configuration values"""
        return self.settings.update_settings(updates, updated_by)
    
    def is_enabled(self) -> bool:
        """Check if bot is enabled"""
        return self.settings.get("enabled", False)
    
    def get_all(self) -> dict:
        """Get all configuration values"""
        return self.settings.get_all()
    
    def reload(self) -> bool:
        """Reload configuration from file"""
        try:
            self.settings.settings = self.settings.load_settings()
            return True
        except Exception:
            return False