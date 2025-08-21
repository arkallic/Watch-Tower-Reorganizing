# managers/moderation/case_manager.py
import os
import json
from datetime import datetime
from typing import Dict, List, Any

class CaseManager:
    def __init__(self, cases_dir: str, user_data: Dict[str, Any], logger):
        self.cases_dir = cases_dir
        self.user_data = user_data
        self.logger = logger
    
    def get_next_case_number(self, user_id: int) -> int:
        """Get the next case number for a user"""
        user_key = str(user_id)
        if user_key not in self.user_data:
            self.user_data[user_key] = {"cases": []}
        
        existing_cases = self.user_data[user_key]["cases"]
        if not existing_cases:
            return 1
        
        return max(case.get("case_number", 0) for case in existing_cases) + 1
    
    def create_case(self, user_id: int, action_data: Dict[str, Any]) -> int:
        """Create a new moderation case"""
        user_key = str(user_id)
        
        # Ensure user entry exists
        if user_key not in self.user_data:
            self.user_data[user_key] = {"cases": []}
        
        # Get case number
        case_number = self.get_next_case_number(user_id)
        
        # Create case data
        case_data = {
            "case_number": case_number,
            "timestamp": datetime.now().isoformat(),
            "status": "Open",
            **action_data  # Merge in the action data
        }
        
        # Add to user data
        self.user_data[user_key]["cases"].append(case_data)
        
        # Save individual case file
        self._save_case_file(user_id, case_number, case_data)
        
        self.logger.console_log_system(
            f"Created case #{case_number} for user {user_id}: {action_data.get('action_type', 'unknown')}",
            "CASE"
        )
        
        return case_number
    
    def get_user_cases(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all cases for a user"""
        user_key = str(user_id)
        return self.user_data.get(user_key, {}).get("cases", [])
    
    def get_case_by_number(self, user_id: int, case_number: int) -> Dict[str, Any]:
        """Get a specific case by number"""
        cases = self.get_user_cases(user_id)
        for case in cases:
            if case.get("case_number") == case_number:
                return case
        return {}
    
    def resolve_case(self, user_id: int, case_number: int, resolution: str, 
                    resolved_by: str) -> bool:
        """Resolve a case"""
        user_key = str(user_id)
        if user_key not in self.user_data:
            return False
        
        cases = self.user_data[user_key]["cases"]
        for case in cases:
            if case.get("case_number") == case_number and case.get("status") == "Open":
                case["status"] = "Resolved"
                case["resolution"] = resolution
                case["resolved_by"] = resolved_by
                case["resolved_at"] = datetime.now().isoformat()
                
                # Update case file
                self._save_case_file(user_id, case_number, case)
                
                self.logger.console_log_system(
                    f"Resolved case #{case_number} for user {user_id}",
                    "CASE"
                )
                return True
        
        return False
    
    def _save_case_file(self, user_id: int, case_number: int, case_data: Dict[str, Any]):
        """Save individual case file"""
        try:
            filename = f"case_{user_id}_{case_number}.json"
            filepath = os.path.join(self.cases_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(case_data, f, indent=2, ensure_ascii=False, default=str)
                
        except Exception as e:
            self.logger.console_log_system(f"Error saving case file: {e}", "ERROR")
    
    def get_open_cases_count(self) -> int:
        """Get total number of open cases across all users"""
        total = 0
        for user_data in self.user_data.values():
            cases = user_data.get("cases", [])
            total += len([c for c in cases if c.get("status") == "Open"])
        return total
    
    def get_cases_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get all cases within a date range"""
        all_cases = []
        
        for user_id, user_data in self.user_data.items():
            cases = user_data.get("cases", [])
            for case in cases:
                try:
                    case_date = datetime.fromisoformat(case.get("timestamp", ""))
                    if start_date <= case_date <= end_date:
                        case_copy = case.copy()
                        case_copy["user_id"] = user_id
                        all_cases.append(case_copy)
                except (ValueError, TypeError):
                    continue
        
        return sorted(all_cases, key=lambda x: x.get("timestamp", ""), reverse=True)