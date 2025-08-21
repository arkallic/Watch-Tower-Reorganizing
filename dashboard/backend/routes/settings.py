from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any, Optional
import aiohttp
import asyncio
from datetime import datetime
import json
import os
from pathlib import Path
from utils.data_manager import DataManager

router = APIRouter(prefix="/settings", tags=["settings"])

@router.get("/")
async def get_all_settings():
    """Get all current settings with enhanced structure"""
    try:
        config = await DataManager.load_config()
        
        guild_info = {}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('http://localhost:8001/bot/guild/info', timeout=5) as response:
                    if response.status == 200:
                        guild_info = await response.json()
        except:
            guild_info = {"channels": {"text_channels": [], "voice_channels": [], "categories": []}, "roles": []}

        settings_schema = {
            "core": {
                "title": "Core Settings",
                "description": "Essential bot configuration and system settings",
                "icon": "shield_check",
                "settings": {
                    "enabled": {
                        "title": "Bot Enabled",
                        "description": "Master switch to enable/disable the entire FlaggerBadger system",
                        "type": "boolean",
                        "current_value": config.get("enabled", False),
                        "default_value": False,
                        "validation": {"required": True},
                        "priority": "critical"
                    },
                    "ai_model_url": {
                        "title": "AI Model URL",
                        "description": "Ollama server endpoint for AI processing",
                        "type": "url",
                        "current_value": config.get("ai_model_url", "http://localhost:11434"),
                        "default_value": "http://localhost:11434",
                        "validation": {"required": True, "format": "url"},
                        "priority": "high"
                    },
                    "time_window_hours": {
                        "title": "Time Window (Hours)",
                        "description": "How many hours to look back when building cases",
                        "type": "integer",
                        "current_value": config.get("time_window_hours", 24),
                        "default_value": 24,
                        "validation": {"min": 1, "max": 168},
                        "priority": "medium"
                    },
                    "messages_per_case": {
                        "title": "Messages Per Case",
                        "description": "Maximum messages to include in a case",
                        "type": "integer",
                        "current_value": config.get("messages_per_case", 10),
                        "default_value": 10,
                        "validation": {"min": 5, "max": 50},
                        "priority": "medium"
                    },
                    "flag_threshold": {
                        "title": "Flag Threshold",
                        "description": "Number of flags required to create a case",
                        "type": "integer",
                        "current_value": config.get("flag_threshold", 7),
                        "default_value": 7,
                        "validation": {"min": 1, "max": 10},
                        "priority": "high"
                    }
                }
            },
            "discord": {
                "title": "Discord Integration",
                "description": "Server channels, roles, and Discord-specific configuration",
                "icon": "server",
                "settings": {
                    "report_channel": {
                        "title": "Report Channel",
                        "description": "Channel where moderation reports are sent",
                        "type": "channel",
                        "current_value": config.get("report_channel"),
                        "default_value": None,
                        "validation": {"required": True},
                        "priority": "critical"
                    },
                    "mod_action_report_channel": {
                        "title": "Mod Action Report Channel",
                        "description": "Channel for moderator action notifications",
                        "type": "channel",
                        "current_value": config.get("mod_action_report_channel"),
                        "default_value": None,
                        "validation": {"required": False},
                        "priority": "medium"
                    },
                    "mod_chat_channel": {
                        "title": "Mod Chat Channel",
                        "description": "Private channel for moderator discussions",
                        "type": "channel",
                        "current_value": config.get("mod_chat_channel"),
                        "default_value": None,
                        "validation": {"required": False},
                        "priority": "medium"
                    },
                    "watch_channels": {
                        "title": "Watch Channels",
                        "description": "Channels to monitor for problematic content",
                        "type": "array",
                        "current_value": config.get("watch_channels", []),
                        "default_value": [],
                        "validation": {"required": False},
                        "priority": "high"
                    },
                    "watch_categories": {
                        "title": "Watch Categories",
                        "description": "Categories to monitor (includes all channels)",
                        "type": "array",
                        "current_value": config.get("watch_categories", []),
                        "default_value": [],
                        "validation": {"required": False},
                        "priority": "medium"
                    }
                }
            },
            "modstrings": {
                "title": "ModString Configuration",
                "description": "Configure ModString pattern matching system",
                "icon": "command_line",
                "settings": {
                    "modstring_enabled": {
                        "title": "ModString Enabled",
                        "description": "Enable ModString pattern matching system",
                        "type": "boolean",
                        "current_value": config.get("modstring_enabled", True),
                        "default_value": True,
                        "validation": {"required": False},
                        "priority": "high"
                    },
                    "modstring_scope": {
                        "title": "ModString Scope",
                        "description": "Choose which channels ModStrings apply to",
                        "type": "select",
                        "current_value": config.get("modstring_scope", "watch_channels"),
                        "default_value": "watch_channels",
                        "validation": {"options": ["watch_channels", "all_channels", "specific_channels"]},
                        "priority": "medium"
                    },
                    "modstring_channels": {
                        "title": "ModString Channels",
                        "description": "Specific channels where ModStrings are active",
                        "type": "array",
                        "current_value": config.get("modstring_channels", []),
                        "default_value": [],
                        "validation": {"required": False},
                        "priority": "medium"
                    },
                    "modstring_action": {
                        "title": "ModString Action",
                        "description": "What to do when a ModString matches",
                        "type": "select",
                        "current_value": config.get("modstring_action", "flag"),
                        "default_value": "flag",
                        "validation": {"options": ["flag", "delete", "timeout", "warn"]},
                        "priority": "high"
                    }
                }
            },
            "monitoring": {
                "title": "AI Monitoring",
                "description": "AI detection, flags, and model configuration",
                "icon": "eye",
                "settings": {
                    "ai_enabled": {
                        "title": "AI Enabled",
                        "description": "Enable AI-powered content analysis",
                        "type": "boolean",
                        "current_value": config.get("ai_enabled", True),
                        "default_value": True,
                        "validation": {"required": False},
                        "priority": "high"
                    },
                    "ai_model": {
                        "title": "AI Model",
                        "description": "Which AI model to use for analysis",
                        "type": "text",
                        "current_value": config.get("ai_model", "llama3.2:3b"),
                        "default_value": "llama3.2:3b",
                        "validation": {"required": False},
                        "priority": "medium"
                    },
                    "ai_confidence_threshold": {
                        "title": "AI Confidence Threshold",
                        "description": "Minimum confidence for AI flags (0-1)",
                        "type": "float",
                        "current_value": config.get("ai_confidence_threshold", 0.7),
                        "default_value": 0.7,
                        "validation": {"min": 0, "max": 1},
                        "priority": "medium"
                    },
                    "ai_auto_moderation": {
                        "title": "AI Auto-moderation",
                        "description": "Allow AI to automatically take moderation actions",
                        "type": "boolean",
                        "current_value": config.get("ai_auto_moderation", False),
                        "default_value": False,
                        "validation": {"required": False},
                        "priority": "high"
                    }
                }
            },
            "permissions": {
                "title": "Permissions & Roles",
                "description": "Configure moderator roles and permissions",
                "icon": "shield_check",
                "settings": {
                    "moderator_roles": {
                        "title": "Moderator Roles",
                        "description": "Roles that can access moderation features",
                        "type": "array",
                        "current_value": config.get("moderator_roles", []),
                        "default_value": [],
                        "validation": {"required": False},
                        "priority": "critical"
                    },
                    "admin_roles": {
                        "title": "Admin Roles",
                        "description": "Roles with full administrative access",
                        "type": "array",
                        "current_value": config.get("admin_roles", []),
                        "default_value": [],
                        "validation": {"required": False},
                        "priority": "high"
                    },
                    "bypass_roles": {
                        "title": "Bypass Roles",
                        "description": "Roles that bypass all moderation checks",
                        "type": "array",
                        "current_value": config.get("bypass_roles", []),
                        "default_value": [],
                        "validation": {"required": False},
                        "priority": "medium"
                    }
                }
            },
            "mental_health": {
                "title": "Mental Health",
                "description": "Support system configuration",
                "icon": "heart",
                "settings": {
                    "mental_health_enabled": {
                        "title": "Mental Health Detection",
                        "description": "Enable mental health crisis detection",
                        "type": "boolean",
                        "current_value": config.get("mental_health_enabled", False),
                        "default_value": False,
                        "validation": {"required": False},
                        "priority": "medium"
                    },
                    "mental_health_alert_channel": {
                        "title": "Mental Health Alert Channel",
                        "description": "Channel for mental health alerts",
                        "type": "channel",
                        "current_value": config.get("mental_health_alert_channel"),
                        "default_value": None,
                        "validation": {"required": False},
                        "priority": "medium"
                    },
                    "mental_health_template": {
                        "title": "Support Template",
                        "description": "Template message for mental health support",
                        "type": "textarea",
                        "current_value": config.get("mental_health_template", ""),
                        "default_value": "",
                        "validation": {"max_length": 2000},
                        "priority": "low"
                    }
                }
            },
            "spotlight": {
                "title": "Spotlight Gate",
                "description": "User verification and screening system",
                "icon": "light_bulb",
                "settings": {
                    "spotlight_enabled": {
                        "title": "Enable Spotlight Gate",
                        "description": "Enable the user verification system",
                        "type": "boolean",
                        "current_value": config.get("spotlight_enabled", False),
                        "default_value": False,
                        "validation": {"required": False},
                        "priority": "medium"
                    },
                    "spotlight_questions": {
                        "title": "Spotlight Questions",
                        "description": "JSON string of verification questions",
                        "type": "text",
                        "current_value": config.get("spotlight_questions", "[]"),
                        "default_value": "[]",
                        "validation": {"required": False},
                        "priority": "medium"
                    },
                    "spotlight_passing_score": {
                        "title": "Passing Score",
                        "description": "Minimum score to pass verification",
                        "type": "number",
                        "current_value": config.get("spotlight_passing_score", 3),
                        "default_value": 3,
                        "validation": {"min": 1, "max": 10},
                        "priority": "medium"
                    },
                    "spotlight_rules": {
                        "title": "Rules Text",
                        "description": "Rules displayed to users",
                        "type": "textarea",
                        "current_value": config.get("spotlight_rules", ""),
                        "default_value": "",
                        "validation": {"max_length": 2000},
                        "priority": "medium"
                    },
                    "spotlight_recaptcha_site_key": {
                        "title": "reCAPTCHA Site Key",
                        "description": "Google reCAPTCHA site key",
                        "type": "text",
                        "current_value": config.get("spotlight_recaptcha_site_key", ""),
                        "default_value": "",
                        "validation": {"required": False},
                        "priority": "low"
                    },
                    "spotlight_captcha_enabled": {
                        "title": "Enable reCAPTCHA",
                        "description": "Require reCAPTCHA verification",
                        "type": "boolean",
                        "current_value": config.get("spotlight_captcha_enabled", False),
                        "default_value": False,
                        "validation": {"required": False},
                        "priority": "low"
                    }
                }
            },
            "advanced": {
                "title": "Advanced",
                "description": "Expert options and tuning",
                "icon": "cog",
                "settings": {
                    "debug_mode": {
                        "title": "Debug Mode",
                        "description": "Enable detailed logging and debugging",
                        "type": "boolean",
                        "current_value": config.get("debug_mode", False),
                        "default_value": False,
                        "validation": {"required": False},
                        "priority": "low"
                    },
                    "api_rate_limit": {
                        "title": "API Rate Limit",
                        "description": "Requests per minute limit for API endpoints",
                        "type": "integer",
                        "current_value": config.get("api_rate_limit", 60),
                        "default_value": 60,
                        "validation": {"min": 10, "max": 1000},
                        "priority": "low"
                    },
                    "auto_backup": {
                        "title": "Auto Backup",
                        "description": "Automatically backup settings and data",
                        "type": "boolean",
                        "current_value": config.get("auto_backup", True),
                        "default_value": True,
                        "validation": {"required": False},
                        "priority": "medium"
                    },
                    "max_case_age_days": {
                        "title": "Max Case Age (Days)",
                        "description": "Automatically archive cases older than this many days",
                        "type": "integer",
                        "current_value": config.get("max_case_age_days", 365),
                        "default_value": 365,
                        "validation": {"min": 30, "max": 3650},
                        "priority": "low"
                    }
                }
            }
        }

        return {
            "settings": settings_schema,
            "metadata": {
                "guild_info": guild_info,
                "last_updated": config.get("last_updated"),
                "updated_by": config.get("updated_by"),
                "config_version": config.get("config_version", "1.0")
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load settings: {str(e)}")

@router.put("/")
async def update_settings(settings_updates: Dict[str, Any]):
    """Update multiple settings"""
    try:
        config = await DataManager.load_config()
        validation_errors = []
        updated_keys = []

        for key, value in settings_updates.items():
            if key in ["enabled", "ai_enabled", "modstring_enabled", "mental_health_enabled", 
                      "spotlight_enabled", "spotlight_captcha_enabled", "ai_auto_moderation", 
                      "debug_mode", "auto_backup"]:
                if not isinstance(value, bool):
                    validation_errors.append(f"{key} must be a boolean")
                else:
                    config[key] = value
                    updated_keys.append(key)
                    
            elif key in ["time_window_hours", "messages_per_case", "flag_threshold", 
                        "spotlight_passing_score", "api_rate_limit", "max_case_age_days"]:
                if not isinstance(value, int):
                    validation_errors.append(f"{key} must be an integer")
                else:
                    config[key] = value
                    updated_keys.append(key)
                    
            elif key in ["ai_confidence_threshold"]:
                if not isinstance(value, (int, float)):
                    validation_errors.append(f"{key} must be a number")
                else:
                    config[key] = float(value)
                    updated_keys.append(key)
                    
            elif key in ["report_channel", "mod_action_report_channel", "mod_chat_channel", 
                        "mental_health_alert_channel"]:
                if value is not None and not isinstance(value, str):
                    validation_errors.append(f"{key} must be a string or null")
                else:
                    config[key] = value
                    updated_keys.append(key)
                    
            elif key in ["watch_channels", "watch_categories", "modstring_channels", 
                        "moderator_roles", "admin_roles", "bypass_roles"]:
                if not isinstance(value, list):
                    validation_errors.append(f"{key} must be an array")
                else:
                    config[key] = value
                    updated_keys.append(key)
                    
            elif key in ["ai_model_url", "ai_model", "modstring_scope", "modstring_action"]:
                if not isinstance(value, str):
                    validation_errors.append(f"{key} must be a string")
                else:
                    config[key] = value
                    updated_keys.append(key)
                    
            elif key in ["mental_health_template", "spotlight_rules", "spotlight_questions", 
                        "spotlight_recaptcha_site_key"]:
                if value is not None and not isinstance(value, str):
                    validation_errors.append(f"{key} must be a string")
                elif value and len(value) > 2000:
                    validation_errors.append(f"{key} must be a string with max 2000 characters")
                else:
                    config[key] = value
                    updated_keys.append(key)
                    
            else:
                validation_errors.append(f"Unknown setting: {key}")
        
        if validation_errors:
            raise HTTPException(status_code=400, detail={
                "message": "Validation errors occurred",
                "errors": validation_errors
            })
        
        await DataManager.save_config(config)
        
        return {
            "success": True,
            "message": f"Successfully updated {len(updated_keys)} settings",
            "updated_keys": updated_keys,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update settings: {str(e)}")

@router.get("/validation")
async def validate_current_settings():
   """Comprehensive validation of all current settings"""
   try:
       config = await DataManager.load_config()
       
       validation_results = {
           "valid": True,
           "errors": [],
           "warnings": [],
           "suggestions": [],
           "system_health": "healthy"
       }
       
       await _validate_core_settings(config, validation_results)
       await _validate_discord_settings(config, validation_results)
       await _validate_modstring_settings(config, validation_results)
       await _validate_ai_settings(config, validation_results)
       await _validate_mental_health_settings(config, validation_results)
       await _validate_advanced_settings(config, validation_results)
       
       if validation_results["errors"]:
           validation_results["system_health"] = "critical"
           validation_results["valid"] = False
       elif validation_results["warnings"]:
           validation_results["system_health"] = "warning"
       
       return validation_results
       
   except Exception as e:
       raise HTTPException(status_code=500, detail=f"Failed to validate settings: {str(e)}")

@router.post("/reset")
async def reset_settings_to_defaults():
   """Reset all settings to their default values"""
   try:
       default_config = {
           "enabled": False,
           "ai_model_url": "http://localhost:11434",
           "time_window_hours": 24,
           "messages_per_case": 10,
           "flag_threshold": 7,
           "debug_mode": False,
           "deleted_message_retention_days": 2,
           "save_deleted_attachments": True,
           "max_attachment_size_mb": 50,
           "report_channel": None,
           "mod_action_report_channel": None,
           "mod_chat_channel": None,
           "ai_enabled": True,
           "ai_model": "llama3.2:3b",
           "ai_confidence_threshold": 0.7,
           "ai_auto_moderation": False,
           "watch_channels": [],
           "watch_categories": [],
           "watch_scope": "specific_channels",
           "modstring_enabled": True,
           "modstring_scope": "watch_channels",
           "modstring_channels": [],
           "modstring_action": "flag",
           "moderator_roles": [],
           "admin_roles": [],
           "bypass_roles": [],
           "mental_health_enabled": False,
           "mental_health_alert_channel": None,
           "mental_health_template": "",
           "spotlight_enabled": False,
           "spotlight_questions": "[]",
           "spotlight_passing_score": 3,
           "spotlight_rules": "",
           "spotlight_recaptcha_site_key": "",
           "spotlight_captcha_enabled": False,
           "api_rate_limit": 60,
           "auto_backup": True,
           "max_case_age_days": 365,
           "last_updated": datetime.now().isoformat(),
           "updated_by": "reset_to_defaults",
           "config_version": "1.0"
       }
       
       await DataManager.save_config(default_config)
       
       return {
           "success": True,
           "message": "Settings reset to default values",
           "timestamp": datetime.now().isoformat()
       }
       
   except Exception as e:
       raise HTTPException(status_code=500, detail=f"Failed to reset settings: {str(e)}")

@router.get("/export")
async def export_settings():
   """Export current settings for backup or transfer"""
   try:
       config = await DataManager.load_config()
       
       export_data = {
           "export_metadata": {
               "exported_at": datetime.now().isoformat(),
               "exported_by": "dashboard",
               "flaggerbadger_version": "2.0",
               "config_version": config.get("config_version", "1.0")
           },
           "settings": config
       }
       
       return export_data
       
   except Exception as e:
       raise HTTPException(status_code=500, detail=f"Failed to export settings: {str(e)}")

@router.get("/spotlight")
async def get_spotlight_settings():
   """Get Spotlight Gate configuration for testing"""
   try:
       config = await DataManager.load_config()
       
       spotlight_settings = {
           "spotlight_enabled": config.get("spotlight_enabled", False),
           "spotlight_rules": config.get("spotlight_rules", ""),
           "spotlight_questions": config.get("spotlight_questions", []),
           "spotlight_recaptcha_site_key": config.get("spotlight_recaptcha_site_key", ""),
           "spotlight_captcha_enabled": config.get("spotlight_captcha_enabled", False),
           "spotlight_passing_score": config.get("spotlight_passing_score", 3),
           "server_name": config.get("server_name", "Discord Server")
       }
       
       return spotlight_settings
       
   except Exception as e:
       raise HTTPException(status_code=500, detail=str(e))

@router.post("/import")
async def import_settings(import_data: Dict[str, Any]):
   """Import settings from backup or transfer"""
   try:
       if "settings" not in import_data:
           raise HTTPException(status_code=400, detail="Invalid import data: missing 'settings' key")
       
       imported_config = import_data["settings"]
       
       validation_errors = await _validate_imported_config(imported_config)
       if validation_errors:
           raise HTTPException(status_code=400, detail={
               "message": "Imported configuration contains errors",
               "errors": validation_errors
           })
       
       imported_config["imported_at"] = datetime.now().isoformat()
       imported_config["imported_by"] = "dashboard"
       imported_config["last_updated"] = datetime.now().isoformat()
       
       await DataManager.save_config(imported_config)
       
       return {
           "success": True,
           "message": "Settings imported successfully",
           "timestamp": datetime.now().isoformat()
       }
       
   except HTTPException:
       raise
   except Exception as e:
       raise HTTPException(status_code=500, detail=f"Failed to import settings: {str(e)}")

@router.get("/history")
async def get_settings_history():
   """Get settings change history"""
   try:
       return {"history": []}
   except Exception as e:
       return {"history": [], "error": str(e)}

@router.get("/health")
async def settings_health_check():
   """Health check for settings system"""
   try:
       config = await DataManager.load_config()
       
       test_config = config.copy()
       test_config["_health_check"] = datetime.now().isoformat()
       await DataManager.save_config(test_config)
       
       del test_config["_health_check"]
       await DataManager.save_config(test_config)
       
       return {
           "status": "healthy",
           "timestamp": datetime.now().isoformat(),
           "config_loaded": True,
           "config_writable": True
       }
       
   except Exception as e:
       raise HTTPException(status_code=500, detail={
           "status": "unhealthy",
           "error": str(e),
           "timestamp": datetime.now().isoformat()
       })

# VALIDATION HELPER FUNCTIONS
async def _validate_core_settings(config: Dict[str, Any], results: Dict[str, Any]):
   """Validate core settings"""
   if not config.get("enabled"):
       results["warnings"].append("Bot is currently disabled")
   
   if not config.get("report_channel"):
       results["errors"].append("No report channel configured")
   
   time_window = config.get("time_window_hours", 24)
   if time_window < 1 or time_window > 168:
       results["errors"].append("Time window must be between 1 and 168 hours")

async def _validate_discord_settings(config: Dict[str, Any], results: Dict[str, Any]):
   """Validate Discord integration settings"""
   if config.get("ai_enabled") and not config.get("watch_channels") and config.get("watch_scope") == "specific_channels":
       results["errors"].append("AI enabled but no channels are being watched")

async def _validate_modstring_settings(config: Dict[str, Any], results: Dict[str, Any]):
   """Validate ModString configuration"""
   if config.get("modstring_enabled") and config.get("modstring_scope") == "specific_channels" and not config.get("modstring_channels"):
       results["warnings"].append("ModString enabled with specific channels but no channels selected")

async def _validate_ai_settings(config: Dict[str, Any], results: Dict[str, Any]):
   """Validate AI monitoring settings"""
   if config.get("ai_enabled"):
       confidence = config.get("ai_confidence_threshold", 0.7)
       if confidence < 0 or confidence > 1:
           results["errors"].append("AI confidence threshold must be between 0 and 1")

async def _validate_mental_health_settings(config: Dict[str, Any], results: Dict[str, Any]):
   """Validate mental health settings"""
   if config.get("mental_health_enabled") and not config.get("mental_health_alert_channel"):
       results["warnings"].append("Mental health detection enabled but no alert channel configured")

async def _validate_advanced_settings(config: Dict[str, Any], results: Dict[str, Any]):
   """Validate advanced settings"""
   if config.get("debug_mode", False):
       results["warnings"].append("Global debug mode is enabled - may impact performance")
   
   if config.get("performance_monitoring", False):
       results["suggestions"].append("Performance monitoring is enabled - check logs for insights")

async def _validate_imported_config(config: Dict[str, Any]) -> List[str]:
   """Validate imported configuration data"""
   errors = []
   
   required_fields = ["enabled", "ai_model_url", "report_channel"]
   for field in required_fields:
       if field not in config:
           errors.append(f"Missing required field: {field}")
   
   type_checks = {
       "enabled": bool,
       "time_window_hours": int,
       "messages_per_case": int,
       "watch_channels": list,
       "moderator_roles": list,
       "flag_threshold": int
   }
   
   for field, expected_type in type_checks.items():
       if field in config and not isinstance(config[field], expected_type):
           errors.append(f"Invalid type for {field}: expected {expected_type.__name__}")
   
   range_checks = {
       "time_window_hours": (1, 168),
       "messages_per_case": (5, 50),
       "flag_threshold": (1, 10)
   }
   
   for field, (min_val, max_val) in range_checks.items():
       if field in config and isinstance(config[field], (int, float)):
           if not min_val <= config[field] <= max_val:
               errors.append(f"Value for {field} must be between {min_val} and {max_val}")
   
   return errors