# api/endpoints/setup.py
from fastapi import APIRouter, HTTPException
from pathlib import Path
import json

router = APIRouter(prefix="/setup", tags=["setup"])

# Global dependencies
bot_settings = None

def initialize_dependencies(bot_settings_instance):
    global bot_settings
    bot_settings = bot_settings_instance

@router.get("/check")
async def check_setup_status():
    """
    Checks if setup is needed - MATCHES ORIGINAL API_calls.py exactly
    1. If bot_settings.json doesn't exist -> First Time.
    2. If bot_settings.json is corrupt (not valid JSON) -> Corruption, trigger setup.
    3. If bot_settings.json is valid -> Not first time.
    """
    settings_file_path = Path(bot_settings.settings_file)
    
    if not settings_file_path.exists():
        return {"isFirstTime": True, "reason": "initial_setup"}

    try:
        with settings_file_path.open('r', encoding='utf-8') as f:
            # Try to load the JSON to check for corruption
            json.load(f)
        # If it loads without error, the file is valid.
        return {"isFirstTime": False}
    except json.JSONDecodeError:
        # The file exists but is broken.
        return {"isFirstTime": True, "reason": "corruption"}
    except Exception as e:
        # Handle other potential file reading errors
        return {"isFirstTime": True, "reason": f"file_error: {e}"}