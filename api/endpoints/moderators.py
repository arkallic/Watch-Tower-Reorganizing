# api/endpoints/moderators.py
from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta

router = APIRouter(tags=["moderators"])

# Global dependencies
bot = None
moderation_manager = None
bot_settings = None

def initialize_dependencies(bot_instance, moderation_manager_instance, bot_settings_instance):
    global bot, moderation_manager, bot_settings
    bot = bot_instance
    moderation_manager = moderation_manager_instance
    bot_settings = bot_settings_instance

@router.get("/moderators")
async def get_moderators():
    """Get moderators with real Discord data, calculated rank, and team summary stats."""
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
                
            mod_cases = [c for c in all_cases if c.get("moderator_id") == member.id]
            total_cases = len(mod_cases)
            
            action_breakdown = {}
            for case in mod_cases:
                action = case.get('action_type', 'mod_note')
                action_breakdown[action] = action_breakdown.get(action, 0) + 1
            
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
    """Provides comprehensive analytics suite for a single moderator."""
    if not bot.is_ready() or not bot.guilds:
        raise HTTPException(status_code=503, detail="Bot not ready")
    
    try:
        guild = bot.guilds[0]
        member = guild.get_member(moderator_id)
        if not member:
            raise HTTPException(status_code=404, detail="Moderator not found in server")

        all_cases = moderation_manager.get_all_cases()
        mod_cases = [c for c in all_cases if c.get("moderator_id") == moderator_id]
        
        now = datetime.now()
        today = now.date()
        start_of_week = today - timedelta(days=today.weekday())
        start_of_month = today.replace(day=1)
        start_of_year = today.replace(month=1, day=1)

        timeline_stats = {"today": 0, "this_week": 0, "this_month": 0, "this_year": 0}
        severity_counts = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}
        action_breakdown = {}
        resolution_times = []
        moderated_users = {}
        activity_heatmap = {}

        for case in mod_cases:
            created_at = datetime.fromisoformat(case['created_at'].replace('Z', ''))
            
            if created_at.date() == today: timeline_stats["today"] += 1
            if created_at.date() >= start_of_week: timeline_stats["this_week"] += 1
            if created_at.date() >= start_of_month: timeline_stats["this_month"] += 1
            if created_at.date() >= start_of_year: timeline_stats["this_year"] += 1
            
            severity = case.get("severity", "Low")
            if severity in severity_counts: severity_counts[severity] += 1
            action = case.get('action_type', 'mod_note')
            action_breakdown[action] = action_breakdown.get(action, 0) + 1

            if case.get("resolved_at"):
                resolved_at = datetime.fromisoformat(case['resolved_at'].replace('Z', ''))
                time_diff_hours = (resolved_at - created_at).total_seconds() / 3600
                resolution_times.append(time_diff_hours)

            user_id = case.get("user_id")
            if user_id:
                if user_id not in moderated_users:
                    moderated_users[user_id] = {"user_id": user_id, "display_name": case.get("display_name", "Unknown"), "case_count": 0}
                moderated_users[user_id]["case_count"] += 1
            
            if created_at > now - timedelta(days=365):
                date_str = created_at.strftime('%Y-%m-%d')
                activity_heatmap[date_str] = activity_heatmap.get(date_str, 0) + 1

        total_mod_cases = len(mod_cases)
        total_server_cases = len(all_cases)
        
        sorted_mod_users = sorted(moderated_users.values(), key=lambda x: x['case_count'], reverse=True)
        
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
                    "by_severity": severity_counts,
                    "by_action": action_breakdown,
                }
            },
            "moderated_users": {
                "most_common": sorted_mod_users[0] if sorted_mod_users else None,
                "list": sorted_mod_users[:20]
            },
            "recent_cases": mod_cases[:20],
            "analytics": {
                 "activity_heatmap": [{"date": date, "count": count} for date, count in activity_heatmap.items()]
            }
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))