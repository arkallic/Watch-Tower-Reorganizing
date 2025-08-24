import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
from colorama import Fore, Style

class AuditLogger:
    """
    Handles the creation and retrieval of structured audit log events for the Timeline.
    """
    def __init__(self, data_dir: str):
        self.log_file = Path(data_dir) / "timeline_events.json"
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Creates the log file with an empty list if it doesn't exist."""
        if not self.log_file.exists():
            try:
                with open(self.log_file, 'w', encoding='utf-8') as f:
                    json.dump([], f)
            except IOError as e:
                print(f"{Fore.RED}❌ Could not create timeline log file: {e}{Style.RESET_ALL}")

    def log_event(
        self,
        event_type: str,
        actor: Dict[str, Any],
        target: Optional[Dict[str, Any]] = None,
        details: Optional[Dict[str, Any]] = None,
        guild: Optional[Any] = None # Optional discord.Guild object
    ):
        """
        Logs a new timeline event.

        Args:
            event_type (str): Unique event identifier (e.g., "MESSAGE_DELETED").
            actor (Dict): Who performed the action. Must include 'id', 'name'. 'avatar' is optional.
            target (Dict, optional): The user/object acted upon.
            details (Dict, optional): Extra context for the event.
            guild (discord.Guild, optional): The guild where the event happened.
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "actor": actor or {},
            "target": target or {},
            "details": details or {},
            "guild_id": str(guild.id) if guild else None
        }

        try:
            with open(self.log_file, 'r+', encoding='utf-8') as f:
                logs = json.load(f)
                logs.insert(0, log_entry) # Prepend for newest-first order
                
                # Trim the log to a max size to prevent it from growing indefinitely
                max_log_size = 5000 
                if len(logs) > max_log_size:
                    logs = logs[:max_log_size]

                f.seek(0)
                json.dump(logs, f, indent=2)
                f.truncate()
        except (IOError, json.JSONDecodeError) as e:
            print(f"{Fore.RED}❌ Error writing to timeline log: {e}{Style.RESET_ALL}")

    def get_logs(self) -> List[Dict[str, Any]]:
        """Retrieves all logs from the timeline file."""
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError):
            return []