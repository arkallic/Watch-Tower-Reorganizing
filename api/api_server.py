# api/api_server.py
import uvicorn
import threading
from .api_app import api_app

def start_api_server():
    """Start the Bot API server on port 8001"""
    try:
        def run_server():
            uvicorn.run(api_app, host="127.0.0.1", port=8001, log_level="info")
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        return True
    except Exception as e:
        print(f"Failed to start API server: {e}")
        return False