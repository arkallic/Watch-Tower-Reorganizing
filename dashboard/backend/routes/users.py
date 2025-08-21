# dashboard/backend/routes/users.py
from fastapi import APIRouter, HTTPException
import httpx

# FIX 1: Added the correct prefix and tags to the router.
# This ensures routes are registered at /api/users/...
router = APIRouter(prefix="/users", tags=["users"])

BOT_API_URL = "http://localhost:8001"

@router.get("/")
async def get_all_users_proxy():
    """
    Acts as a simple proxy to the bot's API to get all users.
    This removes complex logic from the dashboard backend and makes the bot the single source of truth.
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # FIX 2: Forward the request directly to the bot's API.
            response = await client.get(f"{BOT_API_URL}/api/users")
            
            # Forward the exact response (including any errors) from the bot API.
            response.raise_for_status()
            return response.json()
            
    except httpx.RequestError as exc:
        print(f"Error communicating with bot API at /api/users: {exc}")
        raise HTTPException(status_code=502, detail="Error communicating with the bot API.")
    except Exception as e:
        print(f"An unexpected error occurred in get_all_users_proxy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}")
async def get_user_details_proxy(user_id: int):
    """
    Acts as a simple proxy to the bot's API to get details for a specific user.
    This fixes the 404 error and ensures live data is fetched.
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # FIX 3: Forward the request to the correct bot API endpoint for a single user.
            response = await client.get(f"{BOT_API_URL}/api/users/{user_id}")

            # If the bot API returns an error (like 404), forward it.
            if response.status_code != 200:
                # Try to forward the JSON error detail if it exists.
                error_detail = "Not Found"
                try:
                    error_detail = response.json().get("detail", "Not Found")
                except Exception:
                    pass # Keep default error if JSON parsing fails
                raise HTTPException(status_code=response.status_code, detail=error_detail)
            
            return response.json()

    except httpx.RequestError as exc:
        print(f"Error communicating with bot API at /api/users/{user_id}: {exc}")
        raise HTTPException(status_code=502, detail="Error communicating with the bot API.")
    except HTTPException:
        # Re-raise the HTTPException from the try block to preserve status codes
        raise
    except Exception as e:
        print(f"An unexpected error occurred in get_user_details_proxy for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))