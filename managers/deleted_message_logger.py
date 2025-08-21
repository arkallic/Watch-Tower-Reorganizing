# managers/deleted_message_logger.py
import json
import os
import aiohttp
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import discord
from core.settings import bot_settings  
from colorama import Fore, Style

class DeletedMessageLogger:
    def __init__(self):
        # Update path to point to root directory
        self.script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Go up two levels
        self.data_dir = os.path.join(self.script_dir, "data")
        self.attachments_dir = os.path.join(self.data_dir, "deleted_attachments")
        self.deleted_messages_file = os.path.join(self.data_dir, "deleted_messages.json")
        self.max_file_size = 50 * 1024 * 1024  # 50MB limit
        self.ensure_directories()
        self.ensure_log_file_exists()
    
    def ensure_directories(self):
        """Ensure necessary directories exist"""
        directories = [self.data_dir, self.attachments_dir]
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
    
    def ensure_log_file_exists(self):
        """Ensure the deleted messages log file exists"""
        if not os.path.exists(self.deleted_messages_file):
            with open(self.deleted_messages_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
    
    def get_retention_days(self) -> Optional[int]:
        """Get retention days from settings, None means keep forever"""
        retention_days = bot_settings.get("deleted_message_retention_days", 2)
        return retention_days if retention_days > 0 else None
    
    def make_safe_filename(self, filename: str, message_id: int) -> str:
        """Create a safe filename for attachments"""
        # Remove unsafe characters
        safe_chars = []
        for char in filename:
            if char.isalnum() or char in '.-_':
                safe_chars.append(char)
            else:
                safe_chars.append('_')
        
        safe_name = ''.join(safe_chars)
        
        # Add message ID prefix to avoid conflicts
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{message_id}_{timestamp}_{safe_name}"
    
    async def download_attachment(self, attachment: discord.Attachment, message_id: int) -> Dict[str, Any]:
        """Download and save an attachment locally"""
        try:
            # Check if attachment saving is enabled
            if not bot_settings.get("save_deleted_attachments", True):
                return {
                    "filename": attachment.filename,
                    "url": attachment.url,
                    "size": attachment.size,
                    "content_type": getattr(attachment, 'content_type', None),
                    "saved": False,
                    "reason": "Attachment saving disabled in settings"
                }
            
            # Check file size limit
            max_size = bot_settings.get("max_attachment_size_mb", 50) * 1024 * 1024
            if attachment.size > max_size:
                return {
                    "filename": attachment.filename,
                    "url": attachment.url,
                    "size": attachment.size,
                    "content_type": getattr(attachment, 'content_type', None),
                    "saved": False,
                    "error": f"File too large ({attachment.size} bytes > {max_size} limit)"
                }
            
            # Create safe filename
            safe_filename = self.make_safe_filename(attachment.filename, message_id)
            local_path = os.path.join(self.attachments_dir, safe_filename)
            
            # Download the file
            async with aiohttp.ClientSession() as session:
                async with session.get(attachment.url) as response:
                    if response.status == 200:
                        with open(local_path, 'wb') as f:
                            async for chunk in response.content.iter_chunked(1024):
                                f.write(chunk)
                        
                        return {
                            "filename": attachment.filename,
                            "original_url": attachment.url,
                            "local_path": local_path,
                            "safe_filename": safe_filename,
                            "size": attachment.size,
                            "content_type": getattr(attachment, 'content_type', None),
                            "saved": True,
                            "saved_at": datetime.now().isoformat()
                        }
                    else:
                        return {
                            "filename": attachment.filename,
                            "url": attachment.url,
                            "size": attachment.size,
                            "content_type": getattr(attachment, 'content_type', None),
                            "saved": False,
                            "error": f"HTTP {response.status}"
                        }
        
        except Exception as e:
            return {
                "filename": attachment.filename,
                "url": attachment.url,
                "size": attachment.size,
                "content_type": getattr(attachment, 'content_type', None),
                "saved": False,
                "error": str(e)
            }
    
    async def log_deleted_message(self, message: discord.Message):
        """Log a deleted message and download attachments"""
        try:
            # Load existing logs
            with open(self.deleted_messages_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except (json.JSONDecodeError, IOError):
            logs = []
        
        # Download attachments
        saved_attachments = []
        for attachment in message.attachments:
            attachment_data = await self.download_attachment(attachment, message.id)
            saved_attachments.append(attachment_data)
        
        # Create log entry with timezone-naive datetimes
        current_time = datetime.now().replace(tzinfo=None)
        created_time = message.created_at.replace(tzinfo=None) if message.created_at.tzinfo else message.created_at
        
        log_entry = {
            "message_id": message.id,
            "user_id": message.author.id,
            "username": message.author.name,
            "display_name": getattr(message.author, 'display_name', message.author.name),
            "content": message.content,
            "channel_id": message.channel.id,
            "channel_name": message.channel.name,
            "guild_id": message.guild.id if message.guild else None,
            "created_at": created_time.isoformat(),  # Now timezone-naive
            "deleted_at": current_time.isoformat(),  # Now timezone-naive
            "attachments": saved_attachments,
            "embeds_count": len(message.embeds),
            "mentions_count": len(message.mentions),
            "status": "active"
        }
        
        # Add to logs
        logs.append(log_entry)
        
        # Clean up old logs and files (only if retention is enabled)
        retention_days = self.get_retention_days()
        if retention_days is not None:
            self.cleanup_old_logs(logs, retention_days)
        
        # Save updated logs
        try:
            with open(self.deleted_messages_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2, ensure_ascii=False, default=str)
        except IOError as e:
            print(f"{Fore.RED}❌ Error saving deleted message log: {e}{Style.RESET_ALL}")
        
        # Log successful downloads
        downloaded_count = len([att for att in saved_attachments if att.get('saved', False)])
        if downloaded_count > 0:
            print(f"{Fore.GREEN}📎 Saved {downloaded_count}/{len(saved_attachments)} attachments from deleted message{Style.RESET_ALL}")
        
        if bot_settings.get("debug_mode", False):
            print(f"{Fore.CYAN}🗑️ Logged deleted message from {message.author.name} in #{message.channel.name}{Style.RESET_ALL}")
    
    def cleanup_old_logs(self, logs: List[Dict], retention_days: int):
        """Remove logs older than retention_days and delete associated files"""
        cutoff_time = datetime.now() - timedelta(days=retention_days)
        
        # Find logs to remove
        logs_to_remove = []
        for log in logs:
            try:
                deleted_at = datetime.fromisoformat(log["deleted_at"].replace('Z', '+00:00')).replace(tzinfo=None)
                if deleted_at < cutoff_time:
                    logs_to_remove.append(log)
            except (ValueError, KeyError):
                # Invalid date format, remove it
                logs_to_remove.append(log)
        
        # Delete associated files
        for log in logs_to_remove:
            for attachment in log.get("attachments", []):
                if attachment.get("saved") and attachment.get("local_path"):
                    try:
                        if os.path.exists(attachment["local_path"]):
                            os.remove(attachment["local_path"])
                            if bot_settings.get("debug_mode", False):
                                print(f"{Fore.YELLOW}🗑️ Deleted old attachment: {attachment['filename']}{Style.RESET_ALL}")
                    except OSError as e:
                        print(f"{Fore.RED}❌ Failed to delete attachment file: {e}{Style.RESET_ALL}")
        
        # Filter out old logs
        logs[:] = [
            log for log in logs 
            if log not in logs_to_remove
        ]
        
        if logs_to_remove:
            print(f"{Fore.CYAN}🧹 Cleaned up {len(logs_to_remove)} old deleted message logs{Style.RESET_ALL}")
    
    def get_user_deleted_messages(self, user_id: int, hours: int = 48) -> List[Dict]:
        """Get deleted messages for a specific user within the time window"""
        try:
            with open(self.deleted_messages_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except (json.JSONDecodeError, IOError):
            logs = []
        
        # Filter by user and time
        cutoff_time = datetime.now() - timedelta(hours=hours)
        user_deleted_messages = []
        
        for log in logs:
            try:
                if (log["user_id"] == user_id and 
                    datetime.fromisoformat(log["deleted_at"].replace('Z', '+00:00')).replace(tzinfo=None) >= cutoff_time):
                    user_deleted_messages.append(log)
            except (ValueError, KeyError):
                continue
        
        # Sort by deletion time (most recent first)
        user_deleted_messages.sort(key=lambda x: x.get("deleted_at", ""), reverse=True)
        return user_deleted_messages
    
    def get_recent_deletions(self, hours: int = 24) -> List[Dict]:
        """Get all recent deletions within the time window"""
        try:
            with open(self.deleted_messages_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except (json.JSONDecodeError, IOError):
            logs = []
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_deletions = []
        
        for log in logs:
            try:
                if datetime.fromisoformat(log["deleted_at"].replace('Z', '+00:00')).replace(tzinfo=None) >= cutoff_time:
                    recent_deletions.append(log)
            except (ValueError, KeyError):
                continue
        
        # Sort by deletion time (most recent first)
        recent_deletions.sort(key=lambda x: x.get("deleted_at", ""), reverse=True)
        return recent_deletions
    
    def get_stats(self) -> Dict[str, Any]:
        """Get general stats about deleted messages"""
        try:
            with open(self.deleted_messages_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except (json.JSONDecodeError, IOError):
            logs = []
        
        # Count messages by time periods
        now = datetime.now()
        last_24h = now - timedelta(hours=24)
        last_48h = now - timedelta(hours=48)
        last_week = now - timedelta(days=7)
        
        total_deleted = len(logs)
        deleted_24h = 0
        deleted_48h = 0
        deleted_week = 0
        
        for log in logs:
            try:
                deleted_at = datetime.fromisoformat(log["deleted_at"].replace('Z', '+00:00')).replace(tzinfo=None)
                if deleted_at >= last_24h:
                    deleted_24h += 1
                if deleted_at >= last_48h:
                    deleted_48h += 1
                if deleted_at >= last_week:
                    deleted_week += 1
            except (ValueError, KeyError):
                continue
        
        # Count saved attachments
        total_attachments = 0
        saved_attachments = 0
        for log in logs:
            for attachment in log.get("attachments", []):
                total_attachments += 1
                if attachment.get("saved", False):
                    saved_attachments += 1
        
        # Get unique users
        unique_users_24h = set()
        for log in logs:
            try:
                deleted_at = datetime.fromisoformat(log["deleted_at"].replace('Z', '+00:00')).replace(tzinfo=None)
                if deleted_at >= last_24h:
                    unique_users_24h.add(log["user_id"])
            except (ValueError, KeyError):
                continue
        
        # Settings info
        retention_days = self.get_retention_days()
        
        return {
            "total_stored": total_deleted,
            "deleted_last_24h": deleted_24h,
            "deleted_last_48h": deleted_48h,
            "deleted_last_week": deleted_week,
            "unique_users_24h": len(unique_users_24h),
            "total_attachments": total_attachments,
            "saved_attachments": saved_attachments,
            "retention_days": retention_days,
            "retention_enabled": retention_days is not None,
            "settings": {
                "save_attachments": bot_settings.get("save_deleted_attachments", True),
                "max_attachment_size_mb": bot_settings.get("max_attachment_size_mb", 50),
                "debug_mode": bot_settings.get("debug_mode", False)
            }
        }
    
    def manual_cleanup(self) -> Dict[str, int]:
        """Manually trigger cleanup and return statistics"""
        try:
            with open(self.deleted_messages_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"error": "Could not load deleted messages file"}
        
        original_count = len(logs)
        retention_days = self.get_retention_days()
        
        if retention_days is not None:
            self.cleanup_old_logs(logs, retention_days)
            
            # Save cleaned logs
            try:
                with open(self.deleted_messages_file, 'w', encoding='utf-8') as f:
                    json.dump(logs, f, indent=2, ensure_ascii=False, default=str)
            except IOError:
                return {"error": "Could not save cleaned logs"}
        
        cleaned_count = original_count - len(logs)
        
        return {
            "original_count": original_count,
            "remaining_count": len(logs),
            "cleaned_count": cleaned_count,
            "retention_days": retention_days
        }