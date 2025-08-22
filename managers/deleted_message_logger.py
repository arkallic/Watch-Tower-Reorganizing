# managers/deleted_message_logger.py
import json
import os
import aiohttp
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import discord
from core.settings import bot_settings  
from colorama import Fore, Style

################################################################################
# DELETED MESSAGE LOGGER CLASS
################################################################################

class DeletedMessageLogger:
    """Handles the logging, cleanup, and attachment management of deleted Discord messages."""
    
    # --------------------------------------------------------------------------
    # INITIALIZATION & FILE SETUP
    # --------------------------------------------------------------------------
    
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = os.path.join(self.script_dir, "data")
        self.attachments_dir = os.path.join(self.data_dir, "deleted_attachments")
        self.deleted_messages_file = os.path.join(self.data_dir, "deleted_messages.json")
        self.ensure_directories()
        self.ensure_log_file_exists()
    
    def ensure_directories(self):
        """Ensure necessary data and attachment directories exist."""
        for directory in [self.data_dir, self.attachments_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
    
    def ensure_log_file_exists(self):
        """Ensure the deleted messages log file exists to prevent read errors."""
        if not os.path.exists(self.deleted_messages_file):
            with open(self.deleted_messages_file, 'w', encoding='utf-8') as f:
                json.dump([], f)

    # --------------------------------------------------------------------------
    # CORE LOGGING & UPDATE LOGIC
    # --------------------------------------------------------------------------

    async def log_raw_deleted_message(self, payload: discord.RawMessageDeleteEvent):
        """Logs a deleted message from a raw event, which works for cached and uncached messages."""
        try:
            with open(self.deleted_messages_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except (json.JSONDecodeError, IOError):
            logs = []

        message = payload.cached_message
        author = message.author if message else None
        
        saved_attachments = []
        if message:
            for att in message.attachments:
                saved_attachments.append(await self.download_attachment(att, payload.message_id))
        
        log_entry = {
            "message_id": payload.message_id,
            "user_id": author.id if author else None,
            "username": author.name if author else "Unknown (Uncached)",
            "display_name": author.display_name if author else "Unknown (Uncached)",
            "content": message.content if message else "Message content not available (uncached).",
            "channel_id": payload.channel_id,
            "channel_name": str(message.channel) if message else "Unknown",
            "guild_id": payload.guild_id,
            "created_at": message.created_at.isoformat() if message else None,
            "deleted_at": datetime.now().isoformat(),
            "attachments": saved_attachments,
            "deleted_by_id": author.id if author else None,
            "deleted_by_name": author.display_name if author else "Unknown (Likely Self-Delete)",
        }
        logs.append(log_entry)
        self.save_logs(logs)

    async def update_log_with_deleter(self, message_id: int, deleter_id: int, deleter_name: str):
        """Finds a log entry and updates it with the moderator who deleted it."""
        try:
            with open(self.deleted_messages_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            
            log_updated = False
            for log in reversed(logs):
                if log.get("message_id") == message_id:
                    log["deleted_by_id"] = deleter_id
                    log["deleted_by_name"] = deleter_name
                    log_updated = True
                    break
            
            if log_updated:
                self.save_logs(logs)
        except (IOError, json.JSONDecodeError):
            pass

    # --------------------------------------------------------------------------
    # DATA MANAGEMENT & RETRIEVAL
    # --------------------------------------------------------------------------

    def save_logs(self, logs: List[Dict[str, Any]]):
        """Saves the log file and handles cleanup of old entries based on settings."""
        retention_days = bot_settings.get("deleted_message_retention_days", 2)
        if retention_days and retention_days > 0:
            self.cleanup_old_logs(logs, retention_days)
        
        try:
            with open(self.deleted_messages_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2)
        except IOError as e:
            print(f"{Fore.RED}❌ Error saving deleted message log: {e}{Style.RESET_ALL}")

    def cleanup_old_logs(self, logs: List[Dict], retention_days: int):
        """Removes logs and attachments older than the retention period defined in settings."""
        cutoff_time = datetime.now() - timedelta(days=retention_days)
        
        logs_to_keep = []
        logs_to_remove = []
        
        for log in logs:
            try:
                if datetime.fromisoformat(log["deleted_at"]) >= cutoff_time:
                    logs_to_keep.append(log)
                else:
                    logs_to_remove.append(log)
            except (ValueError, KeyError, TypeError):
                # If a log has a bad timestamp, treat it as old to be safe
                logs_to_remove.append(log)
        
        for log in logs_to_remove:
            for attachment in log.get("attachments", []):
                if attachment.get("saved") and (path := attachment.get("local_path")):
                    try:
                        if os.path.exists(path):
                            os.remove(path)
                    except OSError:
                        pass # Ignore errors if file is already gone
        
        logs[:] = logs_to_keep

    def get_user_deleted_messages(self, user_id: int, hours: int = 48) -> List[Dict]:
        """Get deleted messages for a specific user within a time window."""
        try:
            with open(self.deleted_messages_file, 'r', encoding='utf-8') as f:
                all_logs = json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        user_logs = [
            log for log in all_logs
            if str(log.get("user_id")) == str(user_id) and 
               datetime.fromisoformat(log.get("deleted_at")) >= cutoff_time
        ]
        
        user_logs.sort(key=lambda x: x.get("deleted_at", ""), reverse=True)
        return user_logs

    # --------------------------------------------------------------------------
    # ATTACHMENT HANDLING
    # --------------------------------------------------------------------------

    async def download_attachment(self, attachment: discord.Attachment, message_id: int) -> Dict[str, Any]:
        """Downloads and saves an attachment, respecting settings."""
        if not bot_settings.get("save_deleted_attachments", True):
            return {"saved": False, "filename": attachment.filename, "reason": "Attachment saving is disabled in settings."}
        
        max_size = bot_settings.get("max_attachment_size_mb", 50) * 1024 * 1024
        if attachment.size > max_size:
            return {"saved": False, "filename": attachment.filename, "error": f"File is too large ({attachment.size / 1024 / 1024:.2f}MB)."}
        
        safe_filename = f"{message_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{attachment.filename}"
        local_path = os.path.join(self.attachments_dir, safe_filename)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(attachment.url) as response:
                    if response.status == 200:
                        with open(local_path, 'wb') as f:
                            f.write(await response.read())
                        return {
                            "filename": attachment.filename, "local_path": local_path,
                            "size": attachment.size, "saved": True
                        }
                    else:
                        return {"saved": False, "filename": attachment.filename, "error": f"HTTP Error {response.status}"}
        except Exception as e:
            return {"saved": False, "filename": attachment.filename, "error": str(e)}