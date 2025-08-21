# managers/moderation/statistics_manager.py
import csv
import io
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import Counter

class StatisticsManager:
    def __init__(self, user_data: Dict[str, Any]):
        self.user_data = user_data
    
    def get_moderation_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive moderation statistics"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Collect all cases in time period
        recent_cases = []
        for user_id, user_data in self.user_data.items():
            cases = user_data.get("cases", [])
            for case in cases:
                try:
                    case_date = datetime.fromisoformat(case.get("timestamp", ""))
                    if case_date >= cutoff_date:
                        case_copy = case.copy()
                        case_copy["user_id"] = user_id
                        recent_cases.append(case_copy)
                except (ValueError, TypeError):
                    continue
        
        # Calculate statistics
        total_cases = len(recent_cases)
        open_cases = len([c for c in recent_cases if c.get("status") == "Open"])
        resolved_cases = total_cases - open_cases
        
        # Action type breakdown
        action_counts = Counter(case.get("action_type", "unknown") for case in recent_cases)
        
        # Severity breakdown
        severity_counts = Counter(case.get("severity", "Medium") for case in recent_cases)
        
        # Moderator activity
        mod_activity = Counter(case.get("moderator_name", "Unknown") for case in recent_cases)
        
        # Daily activity
        daily_activity = {}
        for case in recent_cases:
            try:
                case_date = datetime.fromisoformat(case.get("timestamp", ""))
                date_key = case_date.strftime("%Y-%m-%d")
                daily_activity[date_key] = daily_activity.get(date_key, 0) + 1
            except (ValueError, TypeError):
                continue
        
        return {
            "period_days": days,
            "total_cases": total_cases,
            "open_cases": open_cases,
            "resolved_cases": resolved_cases,
            "resolution_rate": (resolved_cases / total_cases * 100) if total_cases > 0 else 0,
            "action_breakdown": dict(action_counts),
            "severity_breakdown": dict(severity_counts),
            "moderator_activity": dict(mod_activity.most_common(10)),
            "daily_activity": daily_activity,
            "unique_users_moderated": len(set(case.get("user_id") for case in recent_cases)),
            "avg_cases_per_day": total_cases / days if days > 0 else 0
        }
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Get detailed statistics for a specific user"""
        user_key = str(user_id)
        user_data = self.user_data.get(user_key, {})
        cases = user_data.get("cases", [])
        
        if not cases:
            return {
                "total_cases": 0,
                "open_cases": 0,
                "warns": 0,
                "timeouts": 0,
                "kicks": 0,
                "bans": 0,
                "escalation_level": 0
            }
        
        # Calculate comprehensive stats
        total_cases = len(cases)
        open_cases = len([c for c in cases if c.get("status") == "Open"])
        
        action_counts = Counter(case.get("action_type", "unknown") for case in cases)
        severity_counts = Counter(case.get("severity", "Medium") for case in cases)
        
        # Recent activity (last 30 days)
        cutoff_date = datetime.now() - timedelta(days=30)
        recent_cases = []
        for case in cases:
            try:
                case_date = datetime.fromisoformat(case.get("timestamp", ""))
                if case_date >= cutoff_date:
                    recent_cases.append(case)
            except (ValueError, TypeError):
                continue
        
        # Escalation pattern detection
        escalation_level = len([c for c in cases if c.get("severity") in ["High", "Critical"]])
        
        return {
            "total_cases": total_cases,
            "open_cases": open_cases,
            "warns": action_counts.get("warn", 0),
            "timeouts": action_counts.get("timeout", 0),
            "kicks": action_counts.get("kick", 0),
            "bans": action_counts.get("ban", 0),
            "mod_notes": action_counts.get("mod_note", 0),
            "recent_cases_30d": len(recent_cases),
            "severity_breakdown": dict(severity_counts),
            "escalation_level": escalation_level,
            "last_case_date": cases[-1].get("timestamp") if cases else None,
            "first_case_date": cases[0].get("timestamp") if cases else None,
            "most_common_action": action_counts.most_common(1)[0][0] if action_counts else None,
            "trend": self._calculate_trend(cases)
        }
    
    def get_moderator_stats(self, moderator_name: str, days: int = 30) -> Dict[str, Any]:
        """Get statistics for a specific moderator"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        mod_cases = []
        for user_data in self.user_data.values():
            cases = user_data.get("cases", [])
            for case in cases:
                if case.get("moderator_name") == moderator_name:
                    try:
                        case_date = datetime.fromisoformat(case.get("timestamp", ""))
                        if case_date >= cutoff_date:
                            mod_cases.append(case)
                    except (ValueError, TypeError):
                        continue
        
        if not mod_cases:
            return {"message": "No cases found for this moderator in the specified period"}
        
        action_counts = Counter(case.get("action_type", "unknown") for case in mod_cases)
        severity_counts = Counter(case.get("severity", "Medium") for case in mod_cases)
        
        return {
            "moderator": moderator_name,
            "period_days": days,
            "total_actions": len(mod_cases),
            "actions_per_day": len(mod_cases) / days,
            "action_breakdown": dict(action_counts),
            "severity_breakdown": dict(severity_counts),
            "unique_users_moderated": len(set(case.get("user_id") for case in mod_cases if case.get("user_id")))
        }
    
    def export_cases_to_csv(self, output_file: Optional[str] = None) -> str:
        """Export all cases to CSV format"""
        output = io.StringIO()
        
        # CSV headers
        fieldnames = [
            'user_id', 'case_number', 'timestamp', 'action_type', 'reason',
            'severity', 'moderator_name', 'status', 'duration', 'dm_sent',
            'resolved_at', 'resolved_by', 'resolution'
        ]
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        # Write all cases
        for user_id, user_data in self.user_data.items():
            cases = user_data.get("cases", [])
            for case in cases:
                row = {
                    'user_id': user_id,
                    'case_number': case.get("case_number", ""),
                    'timestamp': case.get("timestamp", ""),
                    'action_type': case.get("action_type", ""),
                    'reason': case.get("reason", ""),
                    'severity': case.get("severity", ""),
                    'moderator_name': case.get("moderator_name", ""),
                    'status': case.get("status", ""),
                    'duration': case.get("duration", ""),
                    'dm_sent': case.get("dm_sent", ""),
                    'resolved_at': case.get("resolved_at", ""),
                    'resolved_by': case.get("resolved_by", ""),
                    'resolution': case.get("resolution", "")
                }
                writer.writerow(row)
        
        csv_content = output.getvalue()
        output.close()
        
        # Save to file if specified
        if output_file:
            try:
                with open(output_file, 'w', newline='', encoding='utf-8') as f:
                    f.write(csv_content)
            except Exception:
                pass  # Ignore file save errors
        
        return csv_content
    
    def _calculate_trend(self, cases: List[Dict[str, Any]]) -> str:
        """Calculate trend direction for a user's cases"""
        if len(cases) < 2:
            return "insufficient_data"
        
        # Look at recent vs older cases
        recent_cutoff = datetime.now() - timedelta(days=30)
        recent_cases = []
        older_cases = []
        
        for case in cases:
            try:
                case_date = datetime.fromisoformat(case.get("timestamp", ""))
                if case_date >= recent_cutoff:
                    recent_cases.append(case)
                else:
                    older_cases.append(case)
            except (ValueError, TypeError):
                continue
        
        if not recent_cases or not older_cases:
            return "insufficient_data"
        
        # Compare severity trends
        recent_severity_avg = self._get_severity_score(recent_cases)
        older_severity_avg = self._get_severity_score(older_cases)
        
        if recent_severity_avg > older_severity_avg * 1.2:
            return "escalating"
        elif recent_severity_avg < older_severity_avg * 0.8:
            return "improving"
        else:
            return "stable"
    
    def _get_severity_score(self, cases: List[Dict[str, Any]]) -> float:
       """Calculate average severity score for a list of cases"""
       if not cases:
           return 0
       
       severity_scores = {
           "Low": 1,
           "Medium": 2,
           "High": 3,
           "Critical": 4
       }
       
       total_score = 0
       for case in cases:
           severity = case.get("severity", "Medium")
           total_score += severity_scores.get(severity, 2)
       
       return total_score / len(cases)