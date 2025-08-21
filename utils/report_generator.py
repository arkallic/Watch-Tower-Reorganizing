# utils/report_generator.py
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from colorama import Fore, Style

class ReportGenerator:
    def __init__(self, moderation_manager):
        self.moderation_manager = moderation_manager
        # Point to root directory
        self.script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Go up two levels
        self.reports_dir = os.path.join(self.script_dir, "reports")
        self.ensure_directories()
    
    def ensure_directories(self):
        """Ensure necessary report directories exist"""
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)
    
    def generate_user_report(self, user_id: int, user_name: str, days_back: int = 30) -> str:
        """Generate a comprehensive user report"""
        try:
            # Get user statistics
            user_stats = self.moderation_manager.statistics_manager.get_user_stats(user_id)
            
            # Generate report filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"user_report_{user_id}_{timestamp}.txt"
            filepath = os.path.join(self.reports_dir, filename)
            
            # Generate report content
            report_lines = [
                "=" * 60,
                f"USER MODERATION REPORT",
                "=" * 60,
                f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"User ID: {user_id}",
                f"Username: {user_name}",
                f"Report Period: Last {days_back} days",
                "",
                "SUMMARY STATISTICS:",
                "-" * 20,
                f"Total Cases: {user_stats.get('total_cases', 0)}",
                f"Open Cases: {user_stats.get('open_cases', 0)}",
                f"Warnings: {user_stats.get('warns', 0)}",
                f"Timeouts: {user_stats.get('timeouts', 0)}",
                f"Kicks: {user_stats.get('kicks', 0)}",
                f"Bans: {user_stats.get('bans', 0)}",
                f"Escalation Level: {user_stats.get('escalation_level', 0)}",
                f"Trend: {user_stats.get('trend', 'Unknown').title()}",
                "",
            ]
            
            # Add case details if available
            user_data = self.moderation_manager.user_data.get(str(user_id), {})
            cases = user_data.get("cases", [])
            
            if cases:
                report_lines.extend([
                    "CASE HISTORY:",
                    "-" * 20,
                ])
                
                for case in sorted(cases, key=lambda x: x.get("timestamp", ""), reverse=True):
                    case_num = case.get("case_number", "Unknown")
                    action = case.get("action_type", "Unknown").title()
                    reason = case.get("reason", "No reason provided")[:50]
                    status = case.get("status", "Unknown")
                    timestamp = case.get("timestamp", "Unknown")
                    
                    report_lines.extend([
                        f"Case #{case_num} - {action} ({status})",
                        f"  Date: {timestamp}",
                        f"  Reason: {reason}",
                        ""
                    ])
            
            # Write report to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(report_lines))
            
            print(f"{Fore.GREEN}✅ User report generated: {filename}{Style.RESET_ALL}")
            return filename
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error generating user report: {e}{Style.RESET_ALL}")
            return ""
    
    def generate_server_report(self, guild_name: str, days_back: int = 30) -> str:
        """Generate a server-wide moderation report"""
        try:
            # Get server statistics
            server_stats = self.moderation_manager.statistics_manager.get_moderation_summary(days_back)
            
            # Generate report filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_guild_name = "".join(c for c in guild_name if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_guild_name = safe_guild_name.replace(' ', '_')
            filename = f"server_report_{safe_guild_name}_{timestamp}.txt"
            filepath = os.path.join(self.reports_dir, filename)
            
            # Generate report content
            report_lines = [
                "=" * 60,
                f"SERVER MODERATION REPORT",
                "=" * 60,
                f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"Server: {guild_name}",
                f"Report Period: Last {days_back} days",
                "",
                "SUMMARY STATISTICS:",
                "-" * 20,
                f"Total Cases: {server_stats.get('total_cases', 0)}",
                f"Open Cases: {server_stats.get('open_cases', 0)}",
                f"Resolved Cases: {server_stats.get('resolved_cases', 0)}",
                f"Resolution Rate: {server_stats.get('resolution_rate', 0):.1f}%",
                f"Unique Users Moderated: {server_stats.get('unique_users_moderated', 0)}",
                f"Average Cases Per Day: {server_stats.get('avg_cases_per_day', 0):.1f}",
                "",
            ]
            
            # Add action breakdown
            action_breakdown = server_stats.get('action_breakdown', {})
            if action_breakdown:
                report_lines.extend([
                    "ACTION BREAKDOWN:",
                    "-" * 20,
                ])
                for action, count in sorted(action_breakdown.items(), key=lambda x: x[1], reverse=True):
                    report_lines.append(f"{action.title()}: {count}")
                report_lines.append("")
            
            # Add moderator activity
            mod_activity = server_stats.get('moderator_activity', {})
            if mod_activity:
                report_lines.extend([
                    "TOP MODERATORS:",
                    "-" * 20,
                ])
                for mod, cases in list(mod_activity.items())[:10]:
                    report_lines.append(f"{mod}: {cases} cases")
                report_lines.append("")
            
            # Write report to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(report_lines))
            
            print(f"{Fore.GREEN}✅ Server report generated: {filename}{Style.RESET_ALL}")
            return filename
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error generating server report: {e}{Style.RESET_ALL}")
            return ""