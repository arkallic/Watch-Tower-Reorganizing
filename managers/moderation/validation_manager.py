# managers/moderation/validation_manager.py
from typing import List

class ValidationManager:
    def __init__(self, settings):
        self.settings = settings
    
    def user_can_moderate(self, user_roles: List[int]) -> bool:
        """Check if user has moderation permissions"""
        mod_roles = self.settings.get("mod_roles", [])
        admin_roles = self.settings.get("admin_roles", [])
        return any(role_id in mod_roles + admin_roles for role_id in user_roles)
    
    def user_is_admin(self, user_roles: List[int]) -> bool:
        """Check if user has admin permissions"""
        admin_roles = self.settings.get("admin_roles", [])
        return any(role_id in admin_roles for role_id in user_roles)
    
    def validate_action_type(self, action_type: str) -> bool:
        """Validate moderation action type"""
        valid_actions = ["warn", "timeout", "kick", "ban", "mod_note", "silence"]
        return action_type in valid_actions
    
    def validate_severity(self, severity: str) -> bool:
        """Validate case severity level"""
        valid_severities = ["Low", "Medium", "High", "Critical"]
        return severity in valid_severities
    
    def validate_duration(self, duration: int, action_type: str) -> bool:
        """Validate duration for time-based actions"""
        if action_type != "timeout":
            return True
        
        # Timeout duration validation (1 minute to 28 days)
        return 1 <= duration <= (28 * 24 * 60)