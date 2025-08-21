# dashboard_auth.py
from typing import List
from core.settings import bot_settings
import discord

class DashboardAuth:
    @staticmethod
    def can_access_dashboard(user_roles: List[int]) -> bool:
        """Check if user can access the dashboard"""
        dashboard_access = bot_settings.get("dashboard_access", "mod_roles_only")
        
        if dashboard_access == "mod_roles_only":
            return bot_settings.user_has_mod_permissions(user_roles)
        elif dashboard_access == "admin_roles_only":
            return bot_settings.user_has_admin_permissions(user_roles)
        elif dashboard_access == "both":
            return (bot_settings.user_has_mod_permissions(user_roles) or 
                   bot_settings.user_has_admin_permissions(user_roles))
        
        return False
    
    @staticmethod
    def get_user_permissions(user_roles: List[int]) -> dict:
        """Get detailed user permissions for the dashboard"""
        return {
            "can_access_dashboard": DashboardAuth.can_access_dashboard(user_roles),
            "is_moderator": bot_settings.user_has_mod_permissions(user_roles),
            "is_admin": bot_settings.user_has_admin_permissions(user_roles),
            "bypasses_checks": bot_settings.user_bypasses_checks(user_roles),
            "access_level": DashboardAuth._get_access_level(user_roles)
        }
    
    @staticmethod
    def _get_access_level(user_roles: List[int]) -> str:
        """Get the user's access level"""
        if bot_settings.user_has_admin_permissions(user_roles):
            return "admin"
        elif bot_settings.user_has_mod_permissions(user_roles):
            return "moderator"
        else:
            return "none"
    
    @staticmethod
    def check_permission_for_action(user_roles: List[int], action: str) -> bool:
        """Check if user has permission for a specific action"""
        user_perms = DashboardAuth.get_user_permissions(user_roles)
        
        # Actions that require admin permissions
        admin_actions = [
            "manage_settings",
            "manage_roles",
            "view_system_logs",
            "export_data",
            "delete_cases",
            "manage_modstrings"
        ]
        
        # Actions that require moderator permissions
        mod_actions = [
            "view_cases",
            "create_cases",
            "resolve_cases",
            "view_flags",
            "manage_users",
            "view_reports"
        ]
        
        if action in admin_actions:
            return user_perms["is_admin"]
        elif action in mod_actions:
            return user_perms["is_moderator"] or user_perms["is_admin"]
        
        # Default: require at least moderator access
        return user_perms["can_access_dashboard"]
    
    @staticmethod
    def get_dashboard_config() -> dict:
        """Get dashboard configuration based on current settings"""
        return {
            "dashboard_access": bot_settings.get("dashboard_access", "mod_roles_only"),
            "mod_roles": bot_settings.get("mod_roles", []),
            "admin_roles": bot_settings.get("admin_roles", []),
            "bypass_roles": bot_settings.get("bypass_roles", []),
            "features_enabled": {
                "moderation": bot_settings.get("enabled", False),
                "ai_monitoring": bot_settings.get("ai_enabled", True),
                "modstrings": bot_settings.get("modstring_enabled", True),
                "reports": True,
                "user_management": True
            }
        }