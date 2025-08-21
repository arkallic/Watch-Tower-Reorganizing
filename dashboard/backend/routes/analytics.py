# dashboard/backend/routes/analytics.py
from fastapi import APIRouter, HTTPException
import httpx

# FIX: Add the correct prefix to match the bot API structure
router = APIRouter(prefix="/analytics", tags=["analytics"])
BOT_API_URL = "http://127.0.0.1:8001"

@router.get("/comprehensive")
async def get_comprehensive_analytics_proxy(days: int = 30):
    """
    Acts as a simple proxy to the bot's API to get comprehensive analytics.
    This ensures the dashboard uses the single source of truth from the bot.
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Forward the request directly to the bot's powerful analytics endpoint
            response = await client.get(f"{BOT_API_URL}/analytics/comprehensive?days={days}")
            
            response.raise_for_status()
            return response.json()
            
    except httpx.RequestError as exc:
        print(f"Error communicating with bot API at /analytics/comprehensive: {exc}")
        raise HTTPException(status_code=502, detail="Error communicating with the bot API.")
    except Exception as e:
        print(f"An unexpected error occurred in get_comprehensive_analytics_proxy: {e}")
        raise HTTPException(status_code=500, detail=str(e))