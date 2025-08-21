# api/endpoints/settings.py
from fastapi import APIRouter, HTTPException
from datetime import datetime

router = APIRouter(prefix="/api/settings", tags=["settings"])

# Global dependencies
bot_settings = None

def initialize_dependencies(bot_settings_instance):
    global bot_settings
    bot_settings = bot_settings_instance

@router.get("/")
async def get_settings():
    """Get current bot settings"""
    try:
        return bot_settings.get_all()
    except Exception as e:
        return {"error": f"Failed to get settings: {str(e)}"}

@router.post("/")
async def update_settings(settings_data: dict):
    """Update bot settings"""
    try:
        success = bot_settings.update_settings(settings_data, "dashboard")
        
        if success:
            return {
                "success": True,
                "message": "Settings updated successfully",
                "updated_settings": settings_data,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {"success": False, "error": "Failed to save settings"}
            
    except Exception as e:
        return {"success": False, "error": f"Failed to update settings: {str(e)}"}

@router.get("/validate")
async def validate_settings():
    """Validate current settings configuration"""
    try:
        settings = bot_settings.get_all()
        issues = []
        
        # Check required settings
        if not settings.get("enabled"):
            issues.append("Bot is disabled")
        
        if not settings.get("report_channel"):
            issues.append("No report channel configured")
        
        if settings.get("ai_enabled") and not settings.get("watch_channels") and settings.get("watch_scope") == "specific_channels":
            issues.append("AI enabled but no channels are being watched")
        
        if not settings.get("mod_roles"):
            issues.append("No moderator roles configured")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "settings_summary": {
                "bot_enabled": settings.get("enabled", False),
                "ai_enabled": settings.get("ai_enabled", False),
                "modstring_enabled": settings.get("modstring_enabled", False),
                "watched_channels": len(settings.get("watch_channels", [])),
                "mod_roles": len(settings.get("mod_roles", []))
            }
        }
        
    except Exception as e:
        return {"error": f"Failed to validate settings: {str(e)}"}

@router.get("/history")
async def get_settings_history():
    """Get settings change history"""
    try:
        history = bot_settings.get_change_history()
        return {"history": history}
    except Exception as e:
        return {"history": [], "error": str(e)}

@router.post("/import")
async def import_settings(data: dict):
    """Import settings from exported data"""
    try:
        if "settings" not in data:
            return {"error": "Invalid import format"}
        
        imported_settings = data["settings"]
        success = bot_settings.update_settings(imported_settings, "dashboard_import")
        
        if success:
            return {"message": f"Successfully imported {len(imported_settings)} settings"}
        else:
            return {"error": "Failed to save imported settings"}
    except Exception as e:
        return {"error": str(e)}

@router.post("/export")
async def export_settings():
    """Export current settings"""
    try:
        current_settings = bot_settings.get_all()
        export_data = {
            "settings": current_settings,
            "exported_at": datetime.now().isoformat(),
            "exported_by": "dashboard_user",
            "version": "1.0"
        }
        return export_data
    except Exception as e:
        return {"error": str(e)}