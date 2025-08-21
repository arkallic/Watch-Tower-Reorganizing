# dashboard/backend/app.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import uvicorn
import httpx
import asyncio
from contextlib import asynccontextmanager

####################
# IMPORTS
####################

try:
    from routes import users, moderators, settings, reports, analytics
    print("✅ All route modules imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")

from utils.data_manager import DataManager

####################
# LIFESPAN EVENTS
####################

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("\n🔍 REGISTERED ROUTES:")
    for route in app.routes:
        if hasattr(route, 'path'):
            methods = getattr(route, 'methods', ['GET'])
            print(f"  {list(methods)[0] if methods else 'GET'} {route.path}")
    print("\n")
    yield
    # Shutdown (if needed)

####################
# APP INITIALIZATION
####################

app = FastAPI(
    title="Watchtower Dashboard API",
    description="API for FlaggerBadger Discord moderation bot dashboard",
    version="2.0.0",
    lifespan=lifespan
)

####################
# CORS CONFIGURATION
####################

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3001",
        "http://127.0.0.1:3001", 
        "http://127.0.0.1:3000",
        "https://watchtower.localdatahost.com",
        "http://watchtower.localdatahost.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

####################
# CONSTANTS
####################

BOT_API_URL = "http://127.0.0.1:8001"

####################
# ROOT ENDPOINT
####################

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Watch Tower Dashboard API",
        "version": "2.0.0",
        "status": "online",
        "docs": "/docs",
        "dashboard": "http://localhost:3000",
        "bot_api": BOT_API_URL
    }

@app.get("/favicon.ico")
async def favicon():
    """Handle favicon requests to prevent 404s"""
    return {"message": "No favicon available"}

####################
# CORE PAGE DATA ENDPOINTS
####################

@app.get("/api/pagedata/dashboard")
async def get_dashboard_data():
    """Get comprehensive dashboard data"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            tasks = [
                client.get(f"{BOT_API_URL}/api/users"),
                client.get(f"{BOT_API_URL}/bot/status"),
                client.get(f"{BOT_API_URL}/bot/guild/info"),
                client.get(f"{BOT_API_URL}/stats/comprehensive"),
                client.get(f"{BOT_API_URL}/moderators"),
                client.get(f"{BOT_API_URL}/system/health")
            ]
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            keys = ["usersData", "botStatus", "guildInfo", "dashboardStats", "moderators", "systemHealth"]
            results = {}
            for i, res in enumerate(responses):
                key = keys[i]
                if isinstance(res, httpx.Response) and res.status_code == 200:
                    results[key] = res.json()
                else:
                    results[key] = {"error": f"Failed to fetch data for {key}"}
            return results
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/pagedata/users")
async def get_users_page_data():
    """Get users page data"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(f"{BOT_API_URL}/api/users")
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as exc:
            raise HTTPException(status_code=502, detail=f"Error communicating with bot API: {exc}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/pagedata/users-growth")
async def get_users_growth_data():
    """Get users growth data"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            tasks = [
                client.get(f"{BOT_API_URL}/stats/activity"),
                client.get(f"{BOT_API_URL}/analytics/trends")
            ]
            activity_res, trends_res = await asyncio.gather(*tasks, return_exceptions=True)
            results = {}
            if isinstance(activity_res, httpx.Response) and activity_res.status_code == 200:
                results["activityData"] = activity_res.json()
            else:
                results["activityData"] = {"error": "Failed to fetch activity"}
            if isinstance(trends_res, httpx.Response) and trends_res.status_code == 200:
                results["trendsData"] = trends_res.json()
            else:
                results["trendsData"] = {"error": "Failed to fetch trends"}
            return results
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/pagedata/cases")
async def get_cases_page_data():
    """Get cases page data"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(f"{BOT_API_URL}/api/cases/enhanced")
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as exc:
            raise HTTPException(status_code=502, detail=f"Error communicating with bot API: {exc}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/pagedata/channels")
async def get_channels_page_data():
    """Get channels page data"""
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            tasks = [
                client.get(f"{BOT_API_URL}/bot/guild/info"),
                client.get(f"{BOT_API_URL}/api/cases/enhanced"),
                client.get(f"{BOT_API_URL}/channels/activity-details"),
                client.get(f"{BOT_API_URL}/stats/deleted-messages")
            ]
            guild_res, cases_res, activity_res, deletions_res = await asyncio.gather(*tasks)

            guild_info = guild_res.json()
            all_cases = cases_res.json().get("cases", [])
            activity_stats = activity_res.json().get("channel_stats", {})
            recent_deletions = deletions_res.json().get("recent_deletions", [])
            
            processed_channels = []
            
            for channel in guild_info.get("channels", {}).get("text_channels", []):
                channel_id_str = str(channel.get("id"))
                
                channel_cases = [case for case in all_cases if str(case.get("channel_id")) == channel_id_str]
                channel_deletions = [d for d in recent_deletions if str(d.get("channel_id")) == channel_id_str]
                stats = activity_stats.get(channel_id_str, {})

                processed_channels.append({
                    **channel,
                    "message_count": stats.get("message_count", 0),
                    "flag_count": stats.get("flag_count", 0),
                    "deletion_count": stats.get("deletion_count", 0),
                    "cases": channel_cases,
                    "case_count": len(channel_cases),
                    "open_case_count": len([c for c in channel_cases if c.get("status") == "Open"]),
                    "recent_deletions": channel_deletions[:10]
                })

            return {"channels": processed_channels}

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

####################
# SPOTLIGHT ENDPOINTS
####################

@app.get("/api/pagedata/spotlight")
async def get_spotlight_page_data():
    """Get spotlight page data including summary and history"""
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            tasks = [
                client.get(f"{BOT_API_URL}/spotlight/summary"),
                client.get(f"{BOT_API_URL}/spotlight/history"),
            ]
            summary_res, history_res = await asyncio.gather(*tasks)
            
            summary_res.raise_for_status()
            history_res.raise_for_status()
            
            return {
                "summary": summary_res.json(),
                "history": history_res.json()
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/gate/config/{user_id}/{key}")
async def get_gate_config(user_id: str, key: str):
    """Proxy for spotlight gate configuration"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(f"{BOT_API_URL}/spotlight/config/{user_id}/{key}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/gate/verify")
async def verify_gate_submission(request: Request):
    """Proxy for spotlight verification"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            body = await request.json()
            # Add client IP to the request
            body["ip"] = request.client.host
            
            response = await client.post(f"{BOT_API_URL}/spotlight/verify", json=body)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/gate/log")
async def log_gate_attempt(request: Request):
    """Proxy for spotlight attempt logging"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            body = await request.json()
            response = await client.post(f"{BOT_API_URL}/spotlight/log", json=body)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/spotlight/decision")
async def make_spotlight_decision(request: Request):
    """Proxy for manual spotlight decisions"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            body = await request.json()
            response = await client.post(f"{BOT_API_URL}/spotlight/manual-decision", json=body)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

####################
# CASE PROXY ENDPOINTS
####################

@app.put("/api/proxy/cases/{user_id}/{case_number}")
async def update_case_proxy(user_id: int, case_number: int, request: Request):
    """Proxy for case updates"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            body = await request.json()
            response = await client.put(f"{BOT_API_URL}/api/cases/{user_id}/{case_number}", json=body)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/proxy/cases/{user_id}/{case_number}")
async def delete_case_proxy(user_id: int, case_number: int):
    """Proxy for case deletion"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.delete(f"{BOT_API_URL}/api/cases/{user_id}/{case_number}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

####################
# SEARCH ENDPOINTS
####################

@app.get("/api/pagedata/search")
async def search_data(q: str = ""):
    """
    Search across users and cases by fetching all data from the bot API and filtering.
    This fixes the 404 error by implementing the search logic here.
    """
    if not q or len(q) < 2:
        return {"users": [], "cases": []}

    search_query = q.lower()

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Step 1: Fetch all users and cases in parallel from the bot API
            users_response_task = client.get(f"{BOT_API_URL}/api/users")
            cases_response_task = client.get(f"{BOT_API_URL}/api/cases/enhanced")
            
            users_response, cases_response = await asyncio.gather(
                users_response_task,
                cases_response_task,
                return_exceptions=True
            )

            # Gracefully handle API fetch errors
            all_users = []
            if not isinstance(users_response, Exception) and users_response.status_code == 200:
                all_users = users_response.json().get("users", [])
            else:
                print(f"Warning: Failed to fetch users for search. Status: {getattr(users_response, 'status_code', 'N/A')}")

            all_cases = []
            if not isinstance(cases_response, Exception) and cases_response.status_code == 200:
                all_cases = cases_response.json().get("cases", [])
            else:
                print(f"Warning: Failed to fetch cases for search. Status: {getattr(cases_response, 'status_code', 'N/A')}")

            # Step 2: Filter users based on the search query
            filtered_users = [
                user for user in all_users
                if search_query in str(user.get("user_id", "")).lower()
                or search_query in str(user.get("display_name", "")).lower()
                or search_query in str(user.get("username", "")).lower()
            ][:10]  # Limit results for performance

            # Step 3: Filter cases based on the search query
            filtered_cases = [
                case for case in all_cases
                if search_query in str(case.get("case_number", "")).lower()
                or search_query in str(case.get("display_name", "")).lower()
                or search_query in str(case.get("reason", "")).lower()
            ][:10]  # Limit results for performance

            # Step 4: Return the combined, filtered results
            return {"users": filtered_users, "cases": filtered_cases}

        except Exception as e:
            print(f"An unexpected error occurred during search: {e}")
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred during search: {e}")

####################
# SETUP ENDPOINTS
####################

@app.get("/api/pagedata/setup-check")
async def check_setup_status():
    """Check if this is first time setup"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(f"{BOT_API_URL}/setup/check")
            return response.json()
        except httpx.RequestError:
            return {"isFirstTime": False, "error": "Bot unreachable"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

####################
# ROUTE REGISTRATION
####################

# Include sub-routers
app.include_router(users.router, prefix="/api")
app.include_router(moderators.router, prefix="/api")
app.include_router(settings.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")

####################
# UTILITY FUNCTIONS
####################

async def process_user_data(user_id: str, data: dict, flagged_messages: list, deleted_messages: list):
    """Process user data for dashboard display"""
    cases = data.get('cases', [])
    open_cases = 0
    resolved_cases = 0
    for case in cases:
        status = case.get('status', 'Open')
        if status in ['Resolved', 'Auto-Resolved']:
            resolved_cases += 1
        else:
            open_cases += 1
    user_flags = [flag for flag in flagged_messages if flag['user_id'] == int(user_id)]
    user_deletions = [msg for msg in deleted_messages if msg['user_id'] == int(user_id)]
    recent_activity = []
    recent_activity.extend([{'type': 'case', 'timestamp': case['timestamp'], 'data': case} for case in cases[-5:]])
    recent_activity.extend([{'type': 'flag', 'timestamp': flag['timestamp'], 'data': flag} for flag in user_flags[-5:]])
    recent_activity.sort(key=lambda x: x['timestamp'], reverse=True)
    total_cases = len(cases)
    risk_score = total_cases * 2 + len(user_flags) * 3 + open_cases * 4
    risk_level = "High" if risk_score >= 20 else "Medium" if risk_score >= 10 else "Low"
    return {
        "id": user_id,
        "name": data.get('display_name', f'User {user_id}'),
        "display_name": data.get('display_name', f'User {user_id}'),
        "total_cases": total_cases,
        "open_cases": open_cases,
        "resolved_cases": resolved_cases,
        "total_flags": len(user_flags),
        "last_case": cases[-1]['timestamp'] if cases else None,
        "risk_level": risk_level,
        "risk_score": risk_score,
        "recent_activity": recent_activity[:10],
        "case_breakdown": {
            'warns': len([c for c in cases if c['action_type'].lower() == 'warn']),
            'timeouts': len([c for c in cases if c['action_type'].lower() == 'timeout']),
            'kicks': len([c for c in cases if c['action_type'].lower() == 'kick']),
            'bans': len([c for c in cases if c['action_type'].lower() == 'ban'])
        }
    }

####################
# MAIN EXECUTION
####################

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Watch Tower Dashboard API...")
    uvicorn.run(app, host="127.0.0.1", port=8000)