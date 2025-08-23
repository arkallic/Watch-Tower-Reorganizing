# dashboard/backend/app.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import uvicorn
import httpx
import asyncio
from contextlib import asynccontextmanager
from collections import Counter

####################
# IMPORTS
####################
try:
    from routes import users, moderators, settings, reports, analytics
    print("✅ All route modules imported successfully")
except ImportError as e:
    print(f"⚠️  Route modules not found, skipping import: {e}")

####################
# LIFESPAN EVENTS
####################
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\n🔍 REGISTERED ROUTES:")
    for route in app.routes:
        if hasattr(route, 'path'):
            methods = getattr(route, 'methods', ['GET'])
            print(f"  {list(methods)[0] if methods else 'GET'} {route.path}")
    print("\n")
    yield

####################
# APP INITIALIZATION
####################
app = FastAPI(
    title="Watchtower Dashboard API",
    description="API for FlaggerBadger Discord moderation bot dashboard",
    version="2.0.0",
    lifespan=lifespan
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://127.0.0.1:3001", "http://127.0.0.1:3000", "https://watchtower.localdatahost.com", "http://watchtower.localdatahost.com"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

BOT_API_URL = "http://127.0.0.1:8001"

####################
# ROOT & HEALTH ENDPOINTS
####################
@app.get("/")
async def root():
    return {"message": "Watch Tower Dashboard API", "version": "2.0.0"}

@app.get("/health")
async def health_check():
    """Simple health check endpoint for the frontend to poll."""
    return {"status": "ok"}

@app.get("/favicon.ico")
async def favicon():
    return {"message": "No favicon available"}

################################
# CORE PAGE DATA ENDPOINTS
################################

@app.get("/api/pagedata/dashboard")
async def get_dashboard_data():
    """
    Get comprehensive dashboard data. This endpoint correctly trusts the Bot API
    to provide pre-calculated, authoritative user stats including risk score.
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            tasks = [
                client.get(f"{BOT_API_URL}/api/users"), client.get(f"{BOT_API_URL}/bot/status"),
                client.get(f"{BOT_API_URL}/bot/guild/info"), client.get(f"{BOT_API_URL}/stats/comprehensive"),
                client.get(f"{BOT_API_URL}/api/cases/enhanced"), client.get(f"{BOT_API_URL}/moderators"),
                client.get(f"{BOT_API_URL}/system/health")
            ]
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            keys = ["usersData", "botStatus", "guildInfo", "dashboardStats", "casesData", "moderators", "systemHealth"]
            raw_data = {keys[i]: (res.json() if isinstance(res, httpx.Response) and res.status_code == 200 else {}) for i, res in enumerate(responses)}
            users = raw_data.get("usersData", {}).get("users", [])
            all_cases = raw_data.get("casesData", {}).get("cases", [])
            guild_info = raw_data.get("guildInfo", {})
            dashboard_stats = raw_data.get("dashboardStats", {})
            bot_status = raw_data.get("botStatus", {})
            moderators_data = raw_data.get("moderators", {})
            human_users = [u for u in users if not u.get('bot')]
            
            processed_stats = {
                "guildName": guild_info.get("guild", {}).get("name", "Server"),
                "totalMembers": guild_info.get("guild", {}).get("member_count", len(users)),
                "humanMembers": len(human_users), "botMembers": len(users) - len(human_users),
                "onlineMembers": len([u for u in users if u.get('status') == 'online']),
                "guildChannels": guild_info.get("channels", {}).get("total_channels", 0),
                "guildRoles": len(guild_info.get("roles", [])), "totalCases": len(all_cases),
                "openCases": len([c for c in all_cases if c.get('status') == 'Open']),
                "cleanUsers": len([u for u in human_users if u.get('total_cases', 0) == 0]),
                "highRiskUsers": len([u for u in human_users if u.get('risk_level') in ['High', 'Critical']]),
                "flaggedUsers": len([u for u in human_users if u.get('total_flags', 0) > 0]),
                "moderatorActivity": moderators_data.get("summary", {}).get("total_moderators", 0),
                "totalDeletions": dashboard_stats.get("deleted_messages", {}).get("last_24h", 0),
                "totalFlags": dashboard_stats.get("general", {}).get("ai_flags", 0), # THIS LINE WAS MISSING
                "messageVelocity": dashboard_stats.get("general", {}).get("messages_per_hour", 0),
                "botOnline": "error" not in bot_status, "botLatency": f"{round(bot_status.get('connection', {}).get('latency', 0))}ms",
            }
            top_users = sorted([u for u in human_users if u.get('total_cases', 0) > 0], key=lambda u: u.get('risk_score', 0), reverse=True)[:5]
            return {"stats": processed_stats, "systemHealth": raw_data.get("systemHealth", {}), "topUsers": top_users}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to process dashboard data: {str(e)}")

@app.get("/api/pagedata/users-enhanced")
async def get_users_page_enhanced_data():
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            tasks = [client.get(f"{BOT_API_URL}/api/users"), client.get(f"{BOT_API_URL}/analytics/trends")]
            users_res, trends_res = await asyncio.gather(*tasks, return_exceptions=True)
            users_data = users_res.json() if isinstance(users_res, httpx.Response) and users_res.status_code == 200 else {}
            trends_data = trends_res.json() if isinstance(trends_res, httpx.Response) and trends_res.status_code == 200 else {}
            users, human_users = users_data.get("users", []), [u for u in users_data.get("users", []) if not u.get('bot')]
            user_stats = {"total": len(users), "humans": len(human_users), "bots": len(users) - len(human_users), "clean": len([u for u in human_users if u.get('total_cases', 0) == 0]), "highRisk": len([u for u in human_users if u.get('risk_level') in ['High', 'Critical']]), "newMembers": len([u for u in human_users if u.get('server_tenure_days', 999) <= 7])}
            risk_distribution = [{"name": lvl, "value": len([u for u in human_users if u.get('risk_level') == lvl]), "color": color} for lvl, color in [('Low', '#22c55e'), ('Medium', '#f59e0b'), ('High', '#ef4444'), ('Critical', '#a855f7')]]
            server_growth = []
            if daily_stats := trends_data.get("daily_stats", []):
                member_count = len(human_users)
                for day in reversed(daily_stats):
                    server_growth.insert(0, {"date": day.get("date"), "members": member_count}); member_count -= (day.get("new_members", 0) - day.get("left_members", 0))
            return {"users": users, "userStats": user_stats, "riskDistribution": [item for item in risk_distribution if item["value"] > 0], "serverGrowth": server_growth}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to process enhanced user data: {str(e)}")

@app.get("/api/pagedata/cases")
async def get_cases_page_data():
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(f"{BOT_API_URL}/api/cases/enhanced")
            response.raise_for_status()
            data = response.json()
            cases = data.get("cases", [])
            now, week_ago = datetime.now(), datetime.now() - timedelta(days=7)
            severity_counts = Counter(c.get("severity", "Low") for c in cases)
            stats = {"total": len(cases), "open": len([c for c in cases if c.get("status") == "Open"]), "resolved": len([c for c in cases if c.get("status") != "Open"]), "critical": severity_counts["Critical"], "thisWeek": len([c for c in cases if c.get("created_at") and datetime.fromisoformat(c["created_at"].replace("Z","")) >= week_ago])}
            daily_data = {(now - timedelta(days=i)).strftime('%Y-%m-%d'): {"name": (now - timedelta(days=i)).strftime('%a'), "Total": 0, "Critical": 0, "Resolved": 0} for i in range(6, -1, -1)}
            for case in cases:
                if dt_str := case.get("created_at"):
                    key = datetime.fromisoformat(dt_str.replace("Z","")).strftime('%Y-%m-%d')
                    if key in daily_data:
                        daily_data[key]["Total"] += 1
                        if case.get("severity") == "Critical": daily_data[key]["Critical"] += 1
                        if case.get("status") != "Open": daily_data[key]["Resolved"] += 1
            severity_data = [{"name": s, "value": v, "color": c} for s, c, v in [("Low", "#22c55e", severity_counts["Low"]), ("Medium", "#f59e0b", severity_counts["Medium"]), ("High", "#ef4444", severity_counts["High"]), ("Critical", "#a855f7", severity_counts["Critical"])]]
            return {"cases": cases, "stats": stats, "chartData": list(daily_data.values()), "severityData": [item for item in severity_data if item["value"] > 0]}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing cases page data: {str(e)}")

@app.get("/api/pagedata/dashboard-chart")
async def get_dashboard_chart_data(range: str = "24h"):
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            tasks = [client.get(f"{BOT_API_URL}/api/cases/enhanced"), client.get(f"{BOT_API_URL}/stats/activity"), client.get(f"{BOT_API_URL}/analytics/trends")]
            cases_res, activity_res, trends_res = await asyncio.gather(*tasks, return_exceptions=True)
            all_cases = cases_res.json().get("cases", []) if isinstance(cases_res, httpx.Response) and cases_res.status_code == 200 else []
            activity_data = activity_res.json() if isinstance(activity_res, httpx.Response) and activity_res.status_code == 200 else {}
            trends_data = trends_res.json() if isinstance(trends_res, httpx.Response) and trends_res.status_code == 200 else {}
            now, labels, data_map = datetime.now(), [], {}
            if range == "24h":
                for i in range(23, -1, -1): labels.append((now - timedelta(hours=i)).strftime("%H:00"))
            else:
                days = 7 if range == "7d" else 30
                for i in range(days - 1, -1, -1): labels.append((now - timedelta(days=i)).strftime("%Y-%m-%d"))
            data_map = {l: {"messages": 0, "cases": 0, "kicks": 0, "bans": 0, "notes": 0} for l in labels}
            for case in all_cases:
                try:
                    if not (dt_str := case.get('created_at')): continue
                    created_at = datetime.fromisoformat(dt_str.replace('Z', ''))
                    key = created_at.strftime("%H:00") if range == "24h" else created_at.strftime("%Y-%m-%d")
                    if key in data_map:
                        data_map[key]["cases"] += 1; action = case.get("action_type", "").lower()
                        if "kick" in action: data_map[key]["kicks"] += 1
                        elif "ban" in action: data_map[key]["bans"] += 1
                        elif "note" in action: data_map[key]["notes"] += 1
                except (ValueError, TypeError): continue
            if range == "24h" and (hourly_data := activity_data.get("hourly_data")):
                for hour in hourly_data:
                    key = f"{str(hour.get('hour')).zfill(2)}:00"
                    if key in data_map: data_map[key]["messages"] = hour.get("messages", 0)
            elif trends_data.get("daily_stats"):
                for day in trends_data["daily_stats"]:
                    if (key := day.get("date")) in data_map: data_map[key]["messages"] = day.get("messages", 0)
            return {"labels": labels, "dataMap": data_map}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to process chart data: {str(e)}")

@app.get("/api/pagedata/channels")
async def get_channels_page_data():
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.get(f"{BOT_API_URL}/stats/channels/comprehensive-summary")
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as exc:
            raise HTTPException(status_code=502, detail=f"Error communicating with bot API: {exc}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing channel page data: {str(e)}")

@app.get("/api/pagedata/user-profile/{user_id}")
async def get_user_profile_page_data(user_id: int):
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(f"{BOT_API_URL}/stats/user-profile/{user_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.json().get("detail"))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch user profile data: {str(e)}")

@app.get("/api/pagedata/moderator-profile/{moderator_id}")
async def get_moderator_profile_page_data(moderator_id: int):
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(f"{BOT_API_URL}/moderators/profile/{moderator_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.json().get("detail"))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch moderator profile data: {str(e)}")

####################
# PROXY & UTILITY ENDPOINTS
####################
@app.post("/api/spotlight/decision")
async def make_spotlight_decision(request: Request):
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            body = await request.json()
            response = await client.post(f"{BOT_API_URL}/spotlight/manual-decision", json=body)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/proxy/cases/{user_id}/{case_number}")
async def update_case_proxy(user_id: int, case_number: int, request: Request):
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
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.delete(f"{BOT_API_URL}/api/cases/{user_id}/{case_number}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/pagedata/search")
async def search_data(q: str = ""):
    if not q or len(q) < 2: return {"users": [], "cases": []}
    search_query = q.lower()
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            users_res, cases_res = await asyncio.gather(client.get(f"{BOT_API_URL}/api/users"), client.get(f"{BOT_API_URL}/api/cases/enhanced"))
            all_users = users_res.json().get("users", []) if users_res.status_code == 200 else []
            all_cases = cases_res.json().get("cases", []) if cases_res.status_code == 200 else []
            filtered_users = [u for u in all_users if search_query in str(u.get("display_name", "")).lower() or search_query in str(u.get("username", "")).lower()][:10]
            filtered_cases = [c for c in all_cases if search_query in str(c.get("case_number", "")).lower() or search_query in str(c.get("reason", "")).lower()][:10]
            return {"users": filtered_users, "cases": filtered_cases}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred during search: {e}")

@app.get("/api/pagedata/setup-check")
async def check_setup_status():
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(f"{BOT_API_URL}/setup/check")
            return response.json()
        except httpx.RequestError:
            return {"isFirstTime": True, "error": "Bot unreachable"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

####################
# ROUTE REGISTRATION
####################
try:
    app.include_router(users.router, prefix="/api")
    app.include_router(moderators.router, prefix="/api")
    app.include_router(settings.router, prefix="/api")
    app.include_router(reports.router, prefix="/api")
    app.include_router(analytics.router, prefix="/api")
except NameError:
    print("ℹ️  Skipping sub-router registration as they were not imported.")

####################
# MAIN EXECUTION
####################
if __name__ == "__main__":
    print("🚀 Starting Watch Tower Dashboard API...")
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)