# api/endpoints/moderators.py
from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
import asyncio
from collections import Counter

router = APIRouter(tags=["moderators"])

# Global dependencies
bot = None
moderation_manager = None
bot_settings = None
activity_tracker = None

def initialize_dependencies(bot_instance, moderation_manager_instance, bot_settings_instance, activity_tracker_instance):
    """Initializes dependencies for the moderators endpoint."""
    global bot, moderation_manager, bot_settings, activity_tracker
    bot = bot_instance
    moderation_manager = moderation_manager_instance
    bot_settings = bot_settings_instance
    activity_tracker = activity_tracker_instance

@router.get("/moderators")
async def get_moderators():
    """ENHANCED: Get moderators with real Discord data, calculated rank, and team summary stats."""
    if not bot.is_ready() or not bot.guilds:
        raise HTTPException(status_code=503, detail="Bot not ready")
    
    try:
        guild = bot.guilds[0]
        mod_role_ids = bot_settings.get("moderator_roles", []) 
        admin_role_ids = bot_settings.get("admin_roles", [])
        all_mod_role_ids = {int(r_id) for r_id in mod_role_ids + admin_role_ids if r_id}

        if not all_mod_role_ids:
            return {"moderators": [], "summary": {"total_moderators": 0, "error": "No moderator roles configured"}}

        all_cases = moderation_manager.get_all_cases()
        
        moderators = []
        for member in guild.members:
            if member.bot: 
                continue
            
            member_role_ids = {role.id for role in member.roles}
            if not all_mod_role_ids.intersection(member_role_ids): 
                continue
                
            mod_cases = [c for c in all_cases if str(c.get("moderator_id")) == str(member.id)]
            total_cases = len(mod_cases)
            
            action_breakdown = Counter(c.get('action_type', 'mod_note') for c in mod_cases)
            efficiency_score = min(100, (total_cases * 2) + (len(action_breakdown) * 5))

            last_activity_ts = None
            if mod_cases:
                case_timestamps = [c.get('created_at') for c in mod_cases if c.get('created_at')]
                if case_timestamps:
                    last_activity_ts = max(case_timestamps)

            moderators.append({
                "moderator_id": str(member.id),
                "name": member.display_name,
                "username": member.name,
                "discriminator": member.discriminator,
                "avatar_url": str(member.display_avatar.url),
                "status": str(member.status),
                "total_cases": total_cases,
                "efficiency_score": round(efficiency_score),
                "last_activity": last_activity_ts,
            })

        moderators.sort(key=lambda m: m['efficiency_score'], reverse=True)
        for i, mod in enumerate(moderators):
            mod['rank'] = i + 1

        total_cases_team = sum(mod['total_cases'] for mod in moderators)
        
        active_mods = 0
        if moderators:
            seven_days_ago = datetime.now() - timedelta(days=7)
            for mod in moderators:
                if mod['last_activity']:
                    last_activity_dt = datetime.fromisoformat(mod['last_activity'].replace('Z', '+00:00')).replace(tzinfo=None)
                    if last_activity_dt > seven_days_ago:
                        active_mods += 1
        
        avg_cases = round(total_cases_team / len(moderators), 1) if moderators else 0

        return {
            "moderators": moderators,
            "summary": {
                "total_moderators": len(moderators),
                "active_moderators_7d": active_mods,
                "total_cases_team": total_cases_team,
                "avg_cases_team": avg_cases
            }
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/moderators/{moderator_id}")
async def get_moderator_details(moderator_id: int):
    """Provides a comprehensive analytics suite for a single moderator."""
    if not bot.is_ready() or not bot.guilds:
        raise HTTPException(status_code=503, detail="Bot not ready")
    
    try:
        guild = bot.guilds[0]
        member = guild.get_member(moderator_id)
        if not member:
            raise HTTPException(status_code=404, detail="Moderator not found in server")

        all_cases = moderation_manager.get_all_cases()
        mod_cases = [c for c in all_cases if str(c.get("moderator_id")) == str(moderator_id)]
        
        now = datetime.now()
        today = now.date()
        start_of_week = today - timedelta(days=today.weekday())
        start_of_month = today.replace(day=1)

        timeline_stats = {"today": 0, "this_week": 0, "this_month": 0}
        resolution_times = []
        activity_heatmap = {}

        for case in mod_cases:
            if case.get('created_at'):
                created_at = datetime.fromisoformat(case['created_at'].replace('Z', ''))
                
                if created_at.date() == today: timeline_stats["today"] += 1
                if created_at.date() >= start_of_week: timeline_stats["this_week"] += 1
                if created_at.date() >= start_of_month: timeline_stats["this_month"] += 1
                
                if case.get("resolved_at"):
                    resolved_at = datetime.fromisoformat(case['resolved_at'].replace('Z', ''))
                    time_diff_hours = (resolved_at - created_at).total_seconds() / 3600
                    resolution_times.append(time_diff_hours)
                
                if created_at > now - timedelta(days=365):
                    date_str = created_at.strftime('%Y-%m-%d')
                    activity_heatmap[date_str] = activity_heatmap.get(date_str, 0) + 1

        total_mod_cases = len(mod_cases)
        total_server_cases = len(all_cases)
        
        action_breakdown = Counter(c.get('action_type', 'mod_note') for c in mod_cases)
        severity_counts = Counter(c.get('severity', 'Low') for c in mod_cases)
        moderated_users = Counter(c.get('display_name', 'Unknown') for c in mod_cases if c.get('display_name'))

        return {
            "profile": {
                "moderator_id": str(member.id),
                "name": member.display_name, 
                "username": member.name,
                "avatar_url": str(member.display_avatar.url),
                "joined_at": member.joined_at.isoformat() if member.joined_at else None,
                "roles": [{"name": r.name, "color": str(r.color)} for r in member.roles if r.name != "@everyone"],
            },
            "stats": {
                "overview": {
                    "total_cases": total_mod_cases,
                    "efficiency_score": min(100, (total_mod_cases * 2) + (len(action_breakdown) * 5)),
                    "percentage_of_total_cases": round((total_mod_cases / total_server_cases) * 100, 1) if total_server_cases > 0 else 0,
                    "unique_users_modded": len(moderated_users),
                },
                "timeline": timeline_stats,
                "performance": {
                    "avg_resolution_hours": round(sum(resolution_times) / len(resolution_times), 1) if resolution_times else None,
                },
                "breakdowns": {
                    "by_severity": dict(severity_counts),
                    "by_action": dict(action_breakdown),
                }
            },
            "moderated_users": {
                "list": [{"name": name, "cases": count} for name, count in moderated_users.most_common(20)]
            },
            "all_cases_by_mod": mod_cases,
            "analytics": {
                 "activity_heatmap": [{"date": date, "count": count} for date, count in activity_heatmap.items()]
            }
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/moderators/profile/{moderator_id}")
async def get_moderator_profile_data(moderator_id: int):
    """
    Provides a comprehensive, all-in-one data payload for a single
    moderator's profile page, including performance, activity, and comparisons.
    """
    if not bot or not bot.guilds:
        raise HTTPException(status_code=503, detail="Bot not connected")

    try:
        details_task = get_moderator_details(moderator_id)
        team_summary_task = get_moderators()
        
        mod_data, team_data = await asyncio.gather(details_task, team_summary_task)
        
        if isinstance(mod_data, HTTPException): raise mod_data
        if isinstance(team_data, HTTPException): raise team_data

        user_activity = activity_tracker.get_user_activity_summary(moderator_id, hours_back=720) # 30 days
        
        # Use the complete case history from the details function
        mod_cases = mod_data.get("all_cases_by_mod", [])
        
        # Calculate Top Modded Channels
        channel_counts = Counter(c.get("channel_name") for c in mod_cases if c.get("channel_name") and c.get("channel_name") != "Unknown")
        top_modded_channels = [{"name": name, "count": count} for name, count in channel_counts.most_common(5)]

        hour_counts = Counter(datetime.fromisoformat(c['created_at'].replace('Z','')).hour for c in mod_cases if c.get('created_at'))
        peak_hour = hour_counts.most_common(1)[0][0] if hour_counts else None
        
        payload = {
            "profile": mod_data.get("profile"),
            "stats": mod_data.get("stats"),
            "analytics": {
                **mod_data.get("analytics", {}),
                "moderator_as_user": {
                    "messages_30d": user_activity.get("messages", 0),
                    "voice_sessions_30d": user_activity.get("voice_sessions", 0),
                    "reactions_30d": user_activity.get("reactions", 0)
                },
                "performance_vs_team": {
                    "team_avg_cases": team_data.get("summary", {}).get("avg_cases_team", 0)
                },
                "top_modded_channels": top_modded_channels,
                "peak_activity_hour_utc": f"{peak_hour}:00 UTC" if peak_hour is not None else "N/A"
            },
            "moderated_users_list": mod_data.get("moderated_users", {}).get("list", []),
            "full_case_history": mod_cases,
        }
        return payload

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))