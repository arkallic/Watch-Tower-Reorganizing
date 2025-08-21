# api/endpoints/statistics.py
from fastapi import APIRouter, HTTPException
from typing import Optional
from datetime import datetime, timedelta
from collections import Counter

router = APIRouter(prefix="/stats", tags=["statistics"])

# Global dependencies
moderation_manager = None
activity_tracker = None
bot = None
deleted_message_logger = None
logger = None

def initialize_dependencies(moderation_manager_instance, activity_tracker_instance, bot_instance, 
                          deleted_message_logger_instance=None, logger_instance=None):
    """Initialize dependencies for statistics endpoint"""
    global moderation_manager, activity_tracker, bot, deleted_message_logger, logger
    moderation_manager = moderation_manager_instance
    activity_tracker = activity_tracker_instance
    bot = bot_instance
    deleted_message_logger = deleted_message_logger_instance
    logger = logger_instance

@router.get("/moderation")
async def get_moderation_stats(days: int = 30):
    """Get comprehensive moderation statistics"""
    try:
        if not moderation_manager:
            return {"error": "Moderation manager not available"}
        
        return moderation_manager.get_moderation_summary(days)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/comprehensive")
async def get_comprehensive_stats(days: int = 30):
    """Get comprehensive statistics combining all data sources - matches original functionality"""
    try:
        if not moderation_manager:
            return {"error": "Moderation manager not available"}
        
        # Get all cases for analysis
        all_cases = moderation_manager.get_all_cases()
        
        # Filter cases by the time range
        cutoff_date = datetime.now() - timedelta(days=days) if days > 0 else datetime.min
        relevant_cases = [
            c for c in all_cases 
            if datetime.fromisoformat(c.get("created_at", "").replace('Z', '')) >= cutoff_date
        ]

        # Initialize overview stats
        overview = {
            "total_cases": len(relevant_cases),
            "open_cases": 0,
            "resolved_cases": 0,
            "resolution_rate": 0.0
        }
        
        # Initialize breakdowns and trends
        breakdowns = {"by_action": Counter(), "by_severity": Counter()}
        leaderboards = {"top_moderators": Counter()}
        trends = {
            "daily_stats": [],
            "peak_day": Counter(),
            "busiest_hour": Counter()
        }

        # Create daily stats structure
        if days > 0:
            for i in range(days):
                date = (cutoff_date + timedelta(days=i)).strftime('%Y-%m-%d')
                trends["daily_stats"].append({"date": date, "cases": 0})

        # Process all relevant cases in a single loop
        for case in relevant_cases:
            try:
                created_at = datetime.fromisoformat(case.get("created_at", "").replace('Z', ''))
                
                # Overview stats
                if case.get("status") == "Open":
                    overview["open_cases"] += 1
                else:
                    overview["resolved_cases"] += 1

                # Breakdowns
                breakdowns["by_action"][case.get("action_type", "unknown")] += 1
                breakdowns["by_severity"][case.get("severity", "Low")] += 1

                # Leaderboards
                mod_name = case.get("moderator_name", "Unknown")
                leaderboards["top_moderators"][mod_name] += 1

                # Trends - daily stats
                case_date = created_at.strftime('%Y-%m-%d')
                for daily_stat in trends["daily_stats"]:
                    if daily_stat["date"] == case_date:
                        daily_stat["cases"] += 1
                        break

                # Trends - peak day and hour
                day_name = created_at.strftime('%A')
                hour = created_at.strftime('%H:00')
                trends["peak_day"][day_name] += 1
                trends["busiest_hour"][hour] += 1

            except (ValueError, TypeError):
                # Skip cases with invalid timestamps
                continue

        # Calculate resolution rate
        if overview["total_cases"] > 0:
            overview["resolution_rate"] = (overview["resolved_cases"] / overview["total_cases"]) * 100

        # Convert counters to sorted lists
        breakdowns_formatted = {
            "by_action": [{"name": action, "value": count} for action, count in breakdowns["by_action"].most_common()],
            "by_severity": [{"name": severity, "value": count} for severity, count in breakdowns["by_severity"].most_common()]
        }

        leaderboards_formatted = {
            "top_moderators": [{"name": mod, "cases": count} for mod, count in leaderboards["top_moderators"].most_common(10)]
        }

        # Get peak day and busiest hour
        peak_day = trends["peak_day"].most_common(1)[0][0] if trends["peak_day"] else "No data"
        busiest_hour = trends["busiest_hour"].most_common(1)[0][0] if trends["busiest_hour"] else "No data"

        # Format final response to match original structure
        comprehensive_stats = {
            "overview": overview,
            "trends": {
                "daily_stats": trends["daily_stats"],
                "peak_day": peak_day,
                "busiest_hour": busiest_hour
            },
            "leaderboards": leaderboards_formatted,
            "breakdowns": breakdowns_formatted,
            "timeframe_days": days,
            "generated_at": datetime.now().isoformat()
        }
        
        return comprehensive_stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/activity")
async def get_activity_stats(days: int = 7):
    """Get user activity statistics"""
    try:
        if not activity_tracker:
            return {"message": "Activity tracking not available"}
        
        # This would need to be implemented in ActivityTracker
        return {"message": "Activity stats endpoint - implementation needed"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export/csv")
async def export_cases_csv():
    """Export moderation cases to CSV"""
    try:
        if not moderation_manager:
            raise HTTPException(status_code=503, detail="Moderation system not available")
        
        csv_content = moderation_manager.export_cases_to_csv()
        
        return {
            "csv_data": csv_content,
            "filename": f"moderation_cases_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))