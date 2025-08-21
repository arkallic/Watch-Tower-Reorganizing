# dashboard/backend/routes/setup.py
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
import aiohttp
import json
import os
from datetime import datetime
from utils.data_manager import DataManager

router = APIRouter()

@router.get("/check")
async def check_first_time_setup():
    """Check if this is the first time setup"""
    try:
        config = await DataManager.load_config()
        
        # Check if essential settings are configured
        is_first_time = not (
            config.get("setup_completed", False) and
            config.get("report_channel") and
            config.get("watch_channels", [])
        )
        
        return {
            "isFirstTime": is_first_time,
            "setupCompleted": config.get("setup_completed", False)
        }
        
    except Exception as e:
        return {"isFirstTime": True, "error": str(e)}

@router.post("/complete")
async def complete_setup(setup_data: Dict[str, Any]):
    """Complete the first time setup with provided configuration"""
    try:
        # Load existing config
        config = await DataManager.load_config()
        
        # Map setup data to config structure
        new_config = {
            **config,
            
            # Core settings
            "enabled": setup_data.get("coreSettings", {}).get("enableBot", True),
            "time_window_hours": setup_data.get("coreSettings", {}).get("timeWindow", 24),
            "messages_per_case": setup_data.get("coreSettings", {}).get("messagesPerCase", 10),
            
            # Channel configuration
            "report_channel": setup_data.get("channels", {}).get("reportChannel"),
            "mod_action_report_channel": setup_data.get("channels", {}).get("modActionReportChannel"),
            "mod_chat_channel": setup_data.get("channels", {}).get("modChatChannel"),
            "watch_channels": setup_data.get("channels", {}).get("watchedChannels", []),
            
            # AI monitoring
            "ai_enabled": setup_data.get("aiMonitoring", {}).get("enabled", True),
            "ai_model_url": setup_data.get("aiMonitoring", {}).get("ollamaEndpoint", "http://127.0.0.1:11434"),
            "ai_model": setup_data.get("aiMonitoring", {}).get("model", "llama3.1"),
            "flag_threshold": setup_data.get("aiMonitoring", {}).get("flagThreshold", 7),
            "custom_prompt": setup_data.get("aiMonitoring", {}).get("customPrompt", ""),
            
            # ModStrings
            "modstrings_enabled": setup_data.get("modStrings", {}).get("enabled", False),
            "modstrings_scope": setup_data.get("modStrings", {}).get("scopeConfig", "PERM"),
            
            # Permissions
            "moderator_roles": setup_data.get("permissions", {}).get("moderatorRoles", []),
            
            # Advanced settings
            "max_case_days": setup_data.get("advanced", {}).get("maxCaseDays", 30),
            "save_deleted_attachments": setup_data.get("advanced", {}).get("saveDeletedAttachments", True),
            "deleted_message_retention": setup_data.get("advanced", {}).get("deletedMessageRetention", 7),
            "max_attachment_size": setup_data.get("advanced", {}).get("maxAttachmentSize"),
            
            # Cases configuration
            "auto_resolve_after": setup_data.get("cases", {}).get("autoResolveAfter", 30),
            "require_moderator_approval": setup_data.get("cases", {}).get("requireModeratorApproval", False),
            
            # Setup metadata
            "setup_completed": True,
            "setup_completed_at": datetime.now().isoformat(),
            "approval_user_id": setup_data.get("approvalUser", {}).get("user_id") if setup_data.get("approvalUser") else None,
            "domain_config": {
                "type": setup_data.get("domain", "localhost"),
                "custom_domain": setup_data.get("customDomain", "")
            }
        }
        
        # Validate essential settings
        if not new_config.get("report_channel"):
            raise HTTPException(status_code=400, detail="Report channel is required")
        
        # Save the configuration
        await DataManager.save_config(new_config)
        
        # If bot should be enabled, notify the bot to reload config
        if new_config.get("enabled", False):
            try:
                async with aiohttp.ClientSession() as session:
                    await session.post('http://localhost:8001/bot/reload-config')
            except:
                pass  # Bot might not be running yet
        
        return {
            "success": True,
            "message": "Setup completed successfully",
            "config_saved": True,
            "bot_enabled": new_config.get("enabled", False)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to complete setup: {str(e)}")

@router.get("/summary")
async def get_setup_summary():
    """Get a summary of the current setup status"""
    try:
        config = await DataManager.load_config()
        
        # Check configuration completeness
        setup_status = {
            "core_configured": bool(config.get("enabled") is not None),
            "channels_configured": bool(config.get("report_channel")),
            "ai_configured": bool(config.get("ai_enabled") is not None),
            "permissions_configured": bool(config.get("moderator_roles")),
            "setup_completed": config.get("setup_completed", False)
        }
        
        # Get configuration summary
        summary = {
            "setupStatus": setup_status,
            "configuration": {
                "botEnabled": config.get("enabled", False),
                "reportChannel": config.get("report_channel"),
                "aiEnabled": config.get("ai_enabled", False),
                "modStringsEnabled": config.get("modstrings_enabled", False),
                "approvalUser": config.get("approval_user_id"),
                "setupCompletedAt": config.get("setup_completed_at")
            },
            "completionPercentage": sum(setup_status.values()) / len(setup_status) * 100
        }
        
        return summary
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get setup summary: {str(e)}")

@router.post("/reset")
async def reset_setup():
    """Reset the setup status (for development/testing)"""
    try:
        config = await DataManager.load_config()
        
        # Remove setup completion markers
        config.pop("setup_completed", None)
        config.pop("setup_completed_at", None)
        
        await DataManager.save_config(config)
        
        return {
            "success": True,
            "message": "Setup status reset successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset setup: {str(e)}")