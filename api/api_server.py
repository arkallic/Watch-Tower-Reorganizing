# api/api_server.py
import threading
import uvicorn
from colorama import Fore, Style

def start_api_server():
    """Start the API server in a separate thread"""
    def run_api():
        try:
            uvicorn.run(
                "api.api_app:api_app",
                host="127.0.0.1",
                port=8001,
                log_level="warning",
                access_log=False
            )
        except Exception as e:
            print(f"{Fore.RED}❌ API server error: {e}{Style.RESET_ALL}")
    
    try:
        api_thread = threading.Thread(target=run_api, daemon=True)
        api_thread.start()
        return True
    except Exception as e:
        print(f"{Fore.RED}❌ Failed to start API server thread: {e}{Style.RESET_ALL}")
        return False