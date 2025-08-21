# api/endpoints/statistics.py
from fastapi import APIRouter, HTTPException
from typing import Optional
from datetime import datetime  # ✅ ADD THIS IMPORT

router = APIRouter(prefix="/stats", tags=["statistics"])

# Global dependencies
moderation_manager = None
activity_tracker = None
bot = None

def initialize_dependencies(moderation_manager_instance, activity_tracker_instance, bot_instance):
    global moderation_manager, activity_tracker, bot
    moderation_manager = moderation_manager_instance
    activity_tracker = activity_tracker_instance
    bot = bot_instance

@router.get("/moderation")
async def get_moderation_stats(days: int = 30):
    """Get comprehensive moderation statistics"""
    try:
        if not moderation_manager:
            return {"error": "Moderation manager not available"}
        
        return moderation_manager.get_moderation_summary(days)
        
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