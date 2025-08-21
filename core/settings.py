# core/settings.py
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from colorama import Fore, Style

####################
# BOTSETTINGS CLASS
####################

class BotSettings:
    def __init__(self):
        # Update path to point to root directory
        self.script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Go up two levels
        self.settings_file = os.path.join(self.script_dir, "bot_settings.json")
        self.settings = self.load_settings()
        self.change_history = []
        
        # Load change history if it exists
        self.history_file = os.path.join(self.script_dir, "settings_history.json")
        self.load_change_history()

    ####################
    # LOADING METHODS
    ####################
    
    def load_settings(self) -> Dict[str, Any]:
        """Load settings from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return self.get_default_settings()
        except Exception as e:
            print(f"{Fore.RED}❌ Error loading settings: {e}{Style.RESET_ALL}")
            return self.get_default_settings()
    
    def load_change_history(self):
        """Load change history from file"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.change_history = json.load(f)
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️ Could not load change history: {e}{Style.RESET_ALL}")
            self.change_history = []
    
    ####################
    # DEFAULT SETTINGS
    ####################
    
    def get_default_settings(self) -> Dict[str, Any]:
        """Get default settings"""
        return {
            # Core settings
            "enabled": False,
            "time_window_hours": 24,
            "messages_per_case": 10,
            "flag_threshold": 7,
            "debug_mode": False,

            # Deleted message settings
            "deleted_message_retention_days": 2,  # 0 = keep forever
            "save_deleted_attachments": True,
            "max_attachment_size_mb": 50,
            
            # Discord integration
            "report_channel": None,
            "mod_action_report_channel": None,
            "mod_chat_channel": None,
            
            # AI monitoring
            "ai_enabled": True,
            "ai_model_url": "http://localhost:11434",
            "watch_channels": [],
            "watch_categories": [],
            "watch_scope": "specific_channels",
            
            # ModString configuration
            "modstring_enabled": True,
            "modstring_scope": "all_channels",
            "modstring_channels": [],
            "modstring_categories": [],
            "modstring_debug": False,
            
            # Permissions and roles
            "mod_roles": [],
            "admin_roles": [],
            "bypass_roles": [],
            "moderator_roles": [],  # ✅ ADDED: Missing from your current file
            "dashboard_access": "mod_roles_only",
            
            # Mental health & Psychosis management
            "mental_health_enabled": False,
            "mental_health_alert_channel": None,
            "mental_health_template": "",
            "psychosis_channel_id": None,  # ✅ ADDED
            "chillzone_category_ids": [],   # ✅ ADDED
            "lounge_channel_id": None,      # ✅ ADDED
            
            # Advanced settings
            "max_case_age_days": 365,
            "api_rate_limit": 60,
            "auto_backup": True,
            "backup_frequency_hours": 24,   # ✅ ADDED
            "last_updated": None,           # ✅ ADDED
            "updated_by": "system",         # ✅ ADDED
            
            ####################
            # SPOTLIGHT SYSTEM
            ####################
            "spotlight_enabled": False,          # ✅ ADDED: Moved out of nested object
            "spotlight_captcha_enabled": True,   # ✅ ADDED: Moved out of nested object  
            "spotlight_questions": "[]",         # ✅ ADDED: Moved out of nested object
            
            # Original nested spotlight object (keep for backward compatibility)
            "spotlight": {
                # Core spotlight settings
                "enabled": False,
                "welcome_channel_id": None,
                "verified_role_id": None,
                
                # reCAPTCHA integration
                "captcha_enabled": True,
                "recaptcha_site_key": "",
                "recaptcha_secret_key": "",
                
                # Security API integrations
                "ip_check_enabled": True,
                "stopforumspam_enabled": True,
                "abuseipdb_enabled": True,
                "ip_api_key": "",
                "abuseipdb_api_key": "",
                
                # Rules and content
                "rules_content": """# Welcome to our server!

Please read our rules carefully before proceeding:

## 📋 Community Guidelines

1. **Be respectful** - Treat all members with kindness and respect
2. **No spam or self-promotion** - Keep discussions relevant 
3. **Use appropriate channels** - Post content in the right places
4. **No NSFW content** - Keep all content family-friendly
5. **Follow Discord ToS** - All Discord rules apply here

## 🛡️ Moderation

- Violations may result in warnings, timeouts, or bans
- Moderators have final say in disputes
- Appeal bans through our support system

By proceeding, you agree to follow these rules.""",
                
                # Quiz configuration
                "passing_score": 3,
                "questions": [
                    {
                        "id": "q1",
                        "text": "What should you do if you want to promote your content?",
                        "options": [
                            "Post it in any channel",
                            "Ask a moderator first",
                            "Don't promote personal content",
                            "Post it multiple times"
                        ],
                        "correct_answer": "Don't promote personal content"
                    },
                    {
                        "id": "q2", 
                        "text": "How should you treat other members?",
                        "options": [
                            "However I want",
                            "With respect and kindness",
                            "Ignore them completely",
                            "Only talk to friends"
                        ],
                        "correct_answer": "With respect and kindness"
                    },
                    {
                        "id": "q3",
                        "text": "What type of content is allowed?",
                        "options": [
                            "Any content",
                            "Only memes", 
                            "Family-friendly content only",
                            "NSFW content in certain channels"
                        ],
                        "correct_answer": "Family-friendly content only"
                    },
                    {
                        "id": "q4",
                        "text": "Who has the final say in disputes?",
                        "options": [
                            "The community",
                            "Server moderators",
                            "Discord support",
                            "The loudest person"
                        ],
                        "correct_answer": "Server moderators"
                    }
                ]
            }
        }

    ####################
    # SAVING METHODS
    ####################
    
    def save_settings(self) -> bool:
        """Save settings to file"""
        try:
            # Update timestamp
            self.settings["last_updated"] = datetime.now().isoformat()
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False, default=str)
            return True
        except Exception as e:
            print(f"{Fore.RED}❌ Error saving settings: {e}{Style.RESET_ALL}")
            return False
    
    def save_change_history(self):
        """Save change history to file"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.change_history, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            print(f"{Fore.RED}❌ Error saving change history: {e}{Style.RESET_ALL}")

    ####################
    # GETTER METHODS
    ####################
    
    def get(self, key: str, default=None):
        """Get a setting value"""
        return self.settings.get(key, default)
    
    def get_all(self) -> Dict[str, Any]:
        """Get all settings"""
        return self.settings.copy()
    
    # ✅ ADDED: Convenience methods for accessing common settings
    def is_enabled(self) -> bool:
        """Check if bot is enabled"""
        return self.get("enabled", False)
    
    def get_report_channel(self) -> Optional[str]:
        """Get report channel ID"""
        return self.get("report_channel")
    
    def get_mod_roles(self) -> List[str]:
        """Get moderator role IDs"""
        return self.get("mod_roles", [])
    
    def get_admin_roles(self) -> List[str]:
        """Get admin role IDs"""
        return self.get("admin_roles", [])

    ####################
    # UPDATE METHODS
    ####################
    
    def update_settings(self, updates: Dict[str, Any], updated_by: str = "system") -> bool:
        """Update multiple settings and track changes"""
        try:
            # Track changes
            changes = {}
            for key, new_value in updates.items():
                old_value = self.settings.get(key)
                if old_value != new_value:
                    changes[key] = {
                        "old": old_value,
                        "new": new_value
                    }
                    self.settings[key] = new_value
            
            # Update metadata
            self.settings["updated_by"] = updated_by
            
            # Save settings
            success = self.save_settings()
            
            # Record change history
            if success and changes:
                self.record_change(changes, updated_by)
                print(f"{Fore.GREEN}✅ Updated {len(changes)} settings{Style.RESET_ALL}")
            
            return success
        except Exception as e:
            print(f"{Fore.RED}❌ Error updating settings: {e}{Style.RESET_ALL}")
            return False
    
    # ✅ ADDED: Individual setting update method
    def set(self, key: str, value: Any, updated_by: str = "system") -> bool:
        """Set a single setting value"""
        return self.update_settings({key: value}, updated_by)

    ####################
    # HISTORY METHODS
    ####################
    
    def record_change(self, changes: Dict[str, Any], updated_by: str):
        """Record a settings change in history"""
        try:
            change_record = {
                "timestamp": datetime.now().isoformat(),
                "updated_by": updated_by,
                "changes": changes,
                "settings_count": len(changes)
            }
            
            self.change_history.append(change_record)
            
            # Keep only last 100 changes
            if len(self.change_history) > 100:
                self.change_history = self.change_history[-100:]
            
            self.save_change_history()
        except Exception as e:
            print(f"{Fore.RED}❌ Error recording change: {e}{Style.RESET_ALL}")
    
    def get_change_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent settings change history"""
        try:
            # Sort by timestamp descending (newest first)
            sorted_history = sorted(
                self.change_history, 
                key=lambda x: x.get('timestamp', ''), 
                reverse=True
            )
            return sorted_history[:limit]
        except Exception as e:
            print(f"{Fore.RED}❌ Error getting change history: {e}{Style.RESET_ALL}")
            return []
    
    def clear_change_history(self) -> bool:
        """Clear settings change history"""
        try:
            self.change_history = []
            return self.save_change_history()
        except Exception as e:
            print(f"{Fore.RED}❌ Error clearing change history: {e}{Style.RESET_ALL}")
            return False

    ####################
    # PERMISSION METHODS
    ####################
    
    def user_has_mod_permissions(self, user_roles: List[int]) -> bool:
        """Check if user has moderator permissions"""
        mod_roles = self.get("mod_roles", [])
        # ✅ ADDED: Also check moderator_roles for backward compatibility
        moderator_roles = self.get("moderator_roles", [])
        all_mod_roles = mod_roles + moderator_roles
        return any(str(role_id) in [str(r) for r in all_mod_roles] for role_id in user_roles)
    
    def user_has_admin_permissions(self, user_roles: List[int]) -> bool:
        """Check if user has admin permissions"""
        admin_roles = self.get("admin_roles", [])
        return any(str(role_id) in [str(r) for r in admin_roles] for role_id in user_roles)
    
    def user_bypasses_checks(self, user_roles: List[int]) -> bool:
        """Check if user bypasses all moderation checks"""
        bypass_roles = self.get("bypass_roles", [])
        return any(str(role_id) in [str(r) for r in bypass_roles] for role_id in user_roles)
    
    def can_access_dashboard(self, user_roles: List[int]) -> bool:
        """Check if user can access the dashboard"""
        dashboard_access = self.get("dashboard_access", "mod_roles_only")
        
        if dashboard_access == "everyone" or dashboard_access == "both":
            return True
        elif dashboard_access == "mod_roles_only":
            return self.user_has_mod_permissions(user_roles) or self.user_has_admin_permissions(user_roles)
        elif dashboard_access == "admin_roles_only":
            return self.user_has_admin_permissions(user_roles)
        else:
            return False

####################
# GLOBAL INSTANCE
####################

# Create global settings instance
bot_settings = BotSettings()