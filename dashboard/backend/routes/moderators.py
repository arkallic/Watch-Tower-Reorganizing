# dashboard/backend/routes/moderators.py
from fastapi import APIRouter, HTTPException
import httpx

router = APIRouter(prefix="/moderators", tags=["moderators"])
BOT_API_URL = "http://localhost:8001"

@router.get("/")
async def get_all_moderators():
    """
    Acts as a simple proxy to the bot's API to get all moderators.
    The bot API is the single source of truth for moderator data and stats.
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{BOT_API_URL}/moderators")
            
            # Forward the response from the bot API directly to the frontend
            response.raise_for_status()
            return response.json()
            
    except httpx.RequestError as exc:
        print(f"Error communicating with bot API: {exc}")
        raise HTTPException(status_code=502, detail="Error communicating with the bot API.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{moderator_id}")
async def get_moderator_details(moderator_id: int):
    """
    Acts as a simple proxy to the bot's API to get details for a specific moderator.
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{BOT_API_URL}/moderators/{moderator_id}")

            # Forward the response, including any errors like 404 Not Found
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.json())
            
            return response.json()

    except httpx.RequestError as exc:
        print(f"Error communicating with bot API: {exc}")
        raise HTTPException(status_code=502, detail="Error communicating with the bot API.")
    except HTTPException:
        # Re-raise HTTPException to preserve status codes from the bot API
        raise
    except Exception as e:
        print(f"An unexpected error occurred in get_moderator_details: {e}")
        raise HTTPException(status_code=500, detail=str(e))