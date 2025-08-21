# api/endpoints/cases.py
from fastapi import APIRouter, HTTPException
from typing import Optional, List
from api.models.api_models import CaseActionRequest

router = APIRouter(prefix="/api/cases", tags=["cases"])

# Global dependencies
moderation_manager = None
bot = None

def initialize_dependencies(moderation_manager_instance, bot_instance):
    global moderation_manager, bot
    moderation_manager = moderation_manager_instance
    bot = bot_instance

@router.get("/")
async def get_cases(user_id: Optional[int] = None, status: Optional[str] = None, limit: int = 100):
    """Get moderation cases with optional filtering"""
    try:
        if not moderation_manager:
            return {"cases": []}
        
        all_cases = []
        
        if user_id:
            # Get cases for specific user
            user_cases = moderation_manager.case_manager.get_user_cases(user_id, status)
            for case in user_cases:
                case["user_id"] = user_id
            all_cases = user_cases
        else:
            # Get all cases
            for uid, user_data in moderation_manager.user_data.items():
                cases = user_data.get("cases", [])
                if status:
                    cases = [case for case in cases if case.get("status") == status]
                
                for case in cases:
                    case["user_id"] = int(uid)
                    all_cases.append(case)
        
        # Sort by creation date (newest first)
        all_cases.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        return {
            "cases": all_cases[:limit],
            "total": len(all_cases)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{user_id}")
async def create_case(user_id: int, case_data: CaseActionRequest):
    """Create a new moderation case"""
    try:
        if not moderation_manager or not bot:
            raise HTTPException(status_code=503, detail="Moderation system not available")
        
        guild = bot.guilds[0] if bot.guilds else None
        if not guild:
            raise HTTPException(status_code=404, detail="No guild connected")
        
        member = guild.get_member(user_id)
        if not member:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Prepare case data
        action_data = {
            "action_type": case_data.action_type,
            "reason": case_data.reason,
            "severity": case_data.severity,
            "duration": case_data.duration,
            "dm_sent": case_data.send_dm,
            "moderator_name": "API",  # This should be updated to use actual moderator
            "display_name": member.display_name,
            "username": member.name
        }
        
        # Create the case
        case_number = await moderation_manager.create_moderation_case(user_id, action_data)
        
        return {
            "success": True,
            "case_number": case_number,
            "message": f"Case #{case_number} created for {member.display_name}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{user_id}/{case_number}/resolve")
async def resolve_case(user_id: int, case_number: int, resolution_comment: str):
    """Resolve a moderation case"""
    try:
        if not moderation_manager:
            raise HTTPException(status_code=503, detail="Moderation system not available")
        
        success = moderation_manager.case_manager.resolve_case(
            user_id, case_number, resolution_comment, "api"
        )
        
        if success:
            moderation_manager.save_user_data()
            return {"success": True, "message": f"Case #{case_number} resolved"}
        else:
            raise HTTPException(status_code=404, detail="Case not found or already resolved")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))