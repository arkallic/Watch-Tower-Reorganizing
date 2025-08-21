# api/endpoints/analytics.py
from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from collections import Counter

router = APIRouter(prefix="/analytics", tags=["analytics"])

# Global dependencies
moderation_manager = None

def initialize_dependencies(moderation_manager_instance, bot_instance=None):
    global moderation_manager, bot
    moderation_manager = moderation_manager_instance
    bot = bot_instance

@router.get("/comprehensive")
async def get_comprehensive_analytics(days: int = 30):
    """Provides comprehensive analytics breakdown for a specified time period - MATCHES ORIGINAL API_calls.py exactly"""
    try:
        all_cases = moderation_manager.get_all_cases()
        
        # Filter cases by the time range
        cutoff_date = datetime.now() - timedelta(days=days) if days > 0 else datetime.min
        relevant_cases = [
            c for c in all_cases 
            if datetime.fromisoformat(c.get("created_at", "").replace('Z', '')) >= cutoff_date
        ]

        # Initialize counters and data structures
        overview = {
            "total_cases": len(relevant_cases),
            "open_cases": 0,
            "resolved_cases": 0,
        }
        breakdowns = {"by_action": Counter(), "by_severity": Counter()}
        leaderboards = {"top_moderators": Counter()}
        trends = {
            "daily_stats": {(cutoff_date + timedelta(days=i)).strftime('%Y-%m-%d'): {"cases": 0} for i in range(days)} if days > 0 else {},
            "peak_day": Counter(),
            "busiest_hour": Counter()
        }

        # Process all relevant cases in a single loop
        for case in relevant_cases:
            created_at = datetime.fromisoformat(case.get("created_at").replace('Z', ''))
            
            # Overview stats
            if case.get("status") == "Open":
                overview["open_cases"] += 1
            else:
                overview["resolved_cases"] += 1

            # Breakdowns
            breakdowns["by_action"][case.get("action_type", "unknown")] += 1
            breakdowns["by_severity"][case.get("severity", "Low")] += 1

            # Leaderboards
            mod_name = case.get("moderator_name", "System")
            if mod_name != "System":
                leaderboards["top_moderators"][mod_name] += 1

            # Trends
            date_str = created_at.strftime('%Y-%m-%d')
            if date_str in trends["daily_stats"]:
                trends["daily_stats"][date_str]["cases"] += 1
            
            trends["peak_day"][created_at.strftime('%A')] += 1
            trends["busiest_hour"][created_at.strftime('%H:00')] += 1

        # Finalize and format the data
        overview["resolution_rate"] = round((overview["resolved_cases"] / overview["total_cases"]) * 100, 1) if overview["total_cases"] > 0 else 0
        
        # Sort daily stats for charting
        trends["daily_stats"] = [{"date": k, **v} for k, v in sorted(trends["daily_stats"].items())]
        
        return {
            "overview": overview,
            "trends": {
                "daily_stats": trends["daily_stats"],
                "peak_day": trends["peak_day"].most_common(1)[0][0] if trends["peak_day"] else "N/A",
                "busiest_hour": trends["busiest_hour"].most_common(1)[0][0] if trends["busiest_hour"] else "N/A",
            },
            "leaderboards": {
                "top_moderators": [{"name": name, "cases": count} for name, count in leaderboards["top_moderators"].most_common(5)]
            },
            "breakdowns": {
                "by_action": [{"name": k, "value": v} for k, v in breakdowns["by_action"].items()],
                "by_severity": [{"name": k, "value": v} for k, v in breakdowns["by_severity"].items()],
            }
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to generate analytics: {str(e)}")

@router.get("/trends")
async def get_analytics_trends():
    """Get trending analytics data - MATCHES ORIGINAL API_calls.py exactly"""
    try:
        guild = bot.guilds[0] if bot and bot.guilds else None
        if not guild:
            return {"error": "No guild connected"}
        
        # Get 7-day trend data
        daily_stats = []
        for i in range(7):
            day_start = datetime.now() - timedelta(days=i)
            daily_stats.append({
                "date": day_start.date().isoformat(),
                "messages": 100,  # Placeholder - implement actual tracking
                "new_members": 0,
                "left_members": 0,
                "cases_created": 0,
                "flags": 0
            })
        
        daily_stats.reverse()  # Chronological order
        
        return {
            "daily_stats": daily_stats,
            "trends": {
                "messages": {"direction": "up", "percentage": 5.2},
                "members": {"direction": "up", "net_change": 3}
            },
            "summary": {
                "total_messages_week": 700,
                "total_new_members": 5,
                "total_cases": 2,
                "total_flags": 10
            }
        }
    except Exception as e:
        return {"error": f"Failed to get analytics trends: {str(e)}"}