import json
import os
import aiofiles
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

class DataManager:
    
    # PATH CONFIGURATION
    BOT_ROOT = Path(__file__).parent.parent.parent.parent
    CASES_PATH = BOT_ROOT / "cases"
    DATA_PATH = BOT_ROOT / "data"
    REPORTS_PATH = BOT_ROOT / "reports"
    CONFIG_PATH = BOT_ROOT / "bot_settings.json"
    
    # CONFIG METHODS
    @staticmethod
    async def load_config():
        """Load bot configuration from bot_settings.json"""
        try:
            async with aiofiles.open(DataManager.CONFIG_PATH, 'r') as f:
                content = await f.read()
                return json.loads(content)
        except FileNotFoundError:
            return DataManager.get_default_config()
    
    @staticmethod
    async def save_config(config_data):
        """Save bot configuration to bot_settings.json"""
        config_data["last_updated"] = datetime.now().isoformat()
        config_data["updated_by"] = "dashboard"
        
        async with aiofiles.open(DataManager.CONFIG_PATH, 'w') as f:
            await f.write(json.dumps(config_data, indent=2))
    
    @staticmethod
    def get_default_config():
        """Get default configuration structure"""
        return {
            "enabled": False,
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
            "ai_model_url": "http://localhost:11434",
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
            "config_version": "1.0"
        }
    
    # CASE MANAGEMENT METHODS
    @staticmethod
    async def load_cases(limit: Optional[int] = None, offset: int = 0) -> List[Dict[str, Any]]:
        """Load cases from disk with pagination"""
        try:
            DataManager.CASES_PATH.mkdir(exist_ok=True)
            cases = []
            
            for case_file in sorted(DataManager.CASES_PATH.glob("*.json"), 
                                  key=lambda x: x.stat().st_mtime, reverse=True):
                try:
                    async with aiofiles.open(case_file, 'r') as f:
                        content = await f.read()
                        case_data = json.loads(content)
                        cases.append(case_data)
                except Exception as e:
                    print(f"Error loading case {case_file}: {e}")
                    continue
            
            if limit:
                return cases[offset:offset + limit]
            return cases[offset:]
            
        except Exception as e:
            print(f"Error loading cases: {e}")
            return []
    
    @staticmethod
    async def save_case(case_data: Dict[str, Any]) -> bool:
        """Save a case to disk"""
        try:
            DataManager.CASES_PATH.mkdir(exist_ok=True)
            case_id = case_data.get("case_id", f"case_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            case_file = DataManager.CASES_PATH / f"{case_id}.json"
            
            case_data["last_updated"] = datetime.now().isoformat()
            
            async with aiofiles.open(case_file, 'w') as f:
                await f.write(json.dumps(case_data, indent=2, default=str))
            
            return True
            
        except Exception as e:
            print(f"Error saving case: {e}")
            return False
    
    @staticmethod
    async def get_case_by_id(case_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific case by ID"""
        try:
            case_file = DataManager.CASES_PATH / f"{case_id}.json"
            if case_file.exists():
                async with aiofiles.open(case_file, 'r') as f:
                    content = await f.read()
                    return json.loads(content)
            return None
            
        except Exception as e:
            print(f"Error loading case {case_id}: {e}")
            return None
    
    @staticmethod
    async def delete_case(case_id: str) -> bool:
        """Delete a case"""
        try:
            case_file = DataManager.CASES_PATH / f"{case_id}.json"
            if case_file.exists():
                case_file.unlink()
                return True
            return False
            
        except Exception as e:
            print(f"Error deleting case {case_id}: {e}")
            return False
    
    # DATA MANAGEMENT METHODS
    @staticmethod
    async def load_user_data(user_id: str) -> Dict[str, Any]:
        """Load user data from disk"""
        try:
            DataManager.DATA_PATH.mkdir(exist_ok=True)
            user_file = DataManager.DATA_PATH / f"user_{user_id}.json"
            
            if user_file.exists():
                async with aiofiles.open(user_file, 'r') as f:
                    content = await f.read()
                    return json.loads(content)
            
            return {
                "user_id": user_id,
                "flags": [],
                "cases": [],
                "notes": [],
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error loading user data for {user_id}: {e}")
            return {}
    
    @staticmethod
    async def save_user_data(user_id: str, user_data: Dict[str, Any]) -> bool:
        """Save user data to disk"""
        try:
            DataManager.DATA_PATH.mkdir(exist_ok=True)
            user_file = DataManager.DATA_PATH / f"user_{user_id}.json"
            
            user_data["last_updated"] = datetime.now().isoformat()
            
            async with aiofiles.open(user_file, 'w') as f:
                await f.write(json.dumps(user_data, indent=2, default=str))
            
            return True
            
        except Exception as e:
            print(f"Error saving user data for {user_id}: {e}")
            return False
    
    @staticmethod
    async def get_all_users(limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all users with their data"""
        try:
            DataManager.DATA_PATH.mkdir(exist_ok=True)
            users = []
            
            for user_file in DataManager.DATA_PATH.glob("user_*.json"):
                try:
                    async with aiofiles.open(user_file, 'r') as f:
                        content = await f.read()
                        user_data = json.loads(content)
                        users.append(user_data)
                except Exception as e:
                    print(f"Error loading user file {user_file}: {e}")
                    continue
            
            users.sort(key=lambda x: x.get("last_updated", ""), reverse=True)
            
            if limit:
                return users[:limit]
            return users
            
        except Exception as e:
            print(f"Error loading users: {e}")
            return []
    
    # REPORT MANAGEMENT METHODS
    @staticmethod
    async def save_report(report_data: Dict[str, Any]) -> bool:
        """Save a report to disk"""
        try:
            DataManager.REPORTS_PATH.mkdir(exist_ok=True)
            report_id = report_data.get("report_id", f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            report_file = DataManager.REPORTS_PATH / f"{report_id}.json"
            
            report_data["created_at"] = datetime.now().isoformat()
            
            async with aiofiles.open(report_file, 'w') as f:
                await f.write(json.dumps(report_data, indent=2, default=str))
            
            return True
            
        except Exception as e:
            print(f"Error saving report: {e}")
            return False
    
    @staticmethod
    async def load_reports(limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Load reports from disk"""
        try:
            DataManager.REPORTS_PATH.mkdir(exist_ok=True)
            reports = []
            
            for report_file in sorted(DataManager.REPORTS_PATH.glob("*.json"), 
                                    key=lambda x: x.stat().st_mtime, reverse=True):
                try:
                    async with aiofiles.open(report_file, 'r') as f:
                        content = await f.read()
                        report_data = json.loads(content)
                        reports.append(report_data)
                except Exception as e:
                    print(f"Error loading report {report_file}: {e}")
                    continue
            
            if limit:
                return reports[:limit]
            return reports
            
        except Exception as e:
            print(f"Error loading reports: {e}")
            return []
    
    # UTILITY METHODS
    @staticmethod
    async def cleanup_old_data(days: int = 30):
        """Clean up old data files"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            for data_path in [DataManager.CASES_PATH, DataManager.DATA_PATH, DataManager.REPORTS_PATH]:
                if not data_path.exists():
                    continue
                    
                for file_path in data_path.glob("*.json"):
                    file_stat = file_path.stat()
                    file_date = datetime.fromtimestamp(file_stat.st_mtime)
                    
                    if file_date < cutoff_date:
                        file_path.unlink()
                        print(f"Deleted old file: {file_path}")
                        
        except Exception as e:
            print(f"Error during cleanup: {e}")
    
    @staticmethod
    async def backup_data(backup_path: Optional[Path] = None):
        """Create a backup of all data"""
        try:
            if backup_path is None:
                backup_path = DataManager.BOT_ROOT / "backups" / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            backup_path.mkdir(parents=True, exist_ok=True)
            
            import shutil
            
            if DataManager.CONFIG_PATH.exists():
                shutil.copy2(DataManager.CONFIG_PATH, backup_path / "bot_settings.json")
            
            for source_dir in [DataManager.CASES_PATH, DataManager.DATA_PATH, DataManager.REPORTS_PATH]:
                if source_dir.exists():
                    dest_dir = backup_path / source_dir.name
                    shutil.copytree(source_dir, dest_dir, dirs_exist_ok=True)
            
            print(f"Backup created at: {backup_path}")
            return True
            
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False