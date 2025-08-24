import asyncio
from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from typing import List, Dict, Any
from . import users as users_endpoint # Import the existing users endpoint to reuse its logic

router = APIRouter(prefix="/cohorts", tags=["cohorts"])

# Global dependencies - will be injected
bot = None
activity_tracker = None

def initialize_dependencies(bot_instance, activity_tracker_instance):
    """Initialize dependencies for this endpoint module"""
    global bot, activity_tracker
    bot = bot_instance
    activity_tracker = activity_tracker_instance

@router.get("/all")
async def get_all_cohorts():
    """
    Analyzes all server members and groups them into dynamic behavioral and social cohorts.
    """
    try:
        # Step 1: Gather all raw data in parallel for maximum efficiency.
        # We run the database-like file reads in threads to avoid blocking the bot.
        users_task = users_endpoint.get_all_users()
        trends_task = asyncio.to_thread(activity_tracker.get_user_activity_trends)
        voice_task = asyncio.to_thread(activity_tracker.get_all_user_voice_time, 30)
        reactions_task = asyncio.to_thread(activity_tracker.get_all_user_reaction_sentiments, 30)
        join_leave_task = asyncio.to_thread(activity_tracker.get_join_leave_history)
        social_task = asyncio.to_thread(activity_tracker.get_social_graph_stats, 30)
        
        # Wait for all data gathering tasks to complete
        user_list_response, activity_trends, voice_times, reaction_sentiments, join_leave_history, social_stats = await asyncio.gather(
            users_task, trends_task, voice_task, reactions_task, join_leave_task, social_task
        )
        
        all_users = user_list_response.get("users", [])
        human_users = [u for u in all_users if not u.get('bot')]

        # Step 2: Enrich each user object with all the new data we just gathered.
        for user in human_users:
            user_id = user['user_id']
            user['activity_trend'] = activity_trends.get(user_id, {})
            user['voice_minutes_30d'] = voice_times.get(user_id, 0)
            user['reactions'] = reaction_sentiments.get(user_id, {'positive': 0, 'negative': 0})
            user['join_leave_history'] = join_leave_history.get(user_id, [])
            user['social_stats'] = social_stats.get(user_id, {})
            # Use a more accurate 30-day message count for sorting
            user['messages_30d'] = user.get('activity_trend', {}).get("messages_last_7d", 0) + round(user.get('activity_trend', {}).get("avg_weekly_messages_30d", 0) * 3)

        # Step 3: Define and process each cohort using the rich user data.
        
        # Original Cohorts (As requested, we are keeping these available)
        new_members = [u for u in human_users if u.get('server_tenure_days', 999) <= 7]
        high_risk_users = [u for u in human_users if u.get('risk_level') in ['High', 'Critical']]
        recently_moderated = [u for u in human_users if u.get('recent_cases', 0) > 0]
        ai_flagged_users = [u for u in human_users if u.get('total_flags', 0) > 0 and u.get('total_cases', 0) == 0]
        clean_record_users = [u for u in human_users if u.get('total_cases', 0) == 0]
        
        # Activity Volume Cohorts
        sorted_by_activity = sorted(human_users, key=lambda u: u.get('messages_30d', 0), reverse=True)
        power_user_count = max(1, len(human_users) // 20) # Top 5%
        lurker_count = max(1, len(human_users) // 10) # Bottom 10%
        power_users = sorted_by_activity[:power_user_count]
        lurkers = [u for u in sorted_by_activity if u.get('messages_30d', 0) <= 2][-lurker_count:]

        # Behavioral Trend Cohorts
        surging_activity = [u for u in human_users if u.get('activity_trend', {}).get('activity_change_percentage', 0) >= 200 and u.get('activity_trend', {}).get('avg_weekly_messages_30d', 0) > 2]
        declining_activity = [u for u in human_users if u.get('activity_trend', {}).get('activity_change_percentage', 0) <= -50 and u.get('activity_trend', {}).get('avg_weekly_messages_30d', 0) > 5]
        anomalous_behavior = [u for u in human_users if u.get('activity_trend', {}).get('new_channels_visited', 0) > 2]

        # New Social & Sentiment Cohorts
        community_uplifters = sorted([u for u in human_users if u['reactions'].get('positive', 0) > 5], key=lambda u: u['reactions'].get('positive', 0), reverse=True)[:max(1, len(human_users)//20)]
        chronic_critics = sorted([u for u in human_users if u['reactions'].get('negative', 0) > 2], key=lambda u: u['reactions'].get('negative', 0), reverse=True)[:max(1, len(human_users)//20)]
        voice_vanguards = sorted([u for u in human_users if u['voice_minutes_30d'] > 60], key=lambda u: u['voice_minutes_30d'], reverse=True)[:max(1, len(human_users)//20)]
        returning_members = [u for u in human_users if len([h for h in u['join_leave_history'] if h['action'] == 'join']) > 1]
        
        community_pillars = sorted(
            [u for u in human_users if (u['social_stats'].get('replies_received', 0) + u['social_stats'].get('mentions_received', 0)) >= 10],
            key=lambda u: (u['social_stats'].get('replies_received', 0) + u['social_stats'].get('mentions_received', 0)),
            reverse=True
        )[:max(1, len(human_users)//20)]

        isolated_members = [
            u for u in human_users if u['messages_30d'] > 5 and
            (u['social_stats'].get('replies_received', 0) + u['social_stats'].get('mentions_received', 0)) == 0
        ]

        # Step 4: Assemble the final payload for the frontend.
        def get_cohort_stats(cohort):
            if not cohort: return {"user_count": 0, "avg_risk_score": 0, "total_cases": 0}
            user_count = len(cohort)
            return {
                "user_count": user_count,
                "avg_risk_score": round(sum(u.get('risk_score', 0) for u in cohort) / user_count) if user_count > 0 else 0,
                "total_cases": sum(u.get('total_cases', 0) for u in cohort)
            }

        return {
            "summary": {
                "new_members": get_cohort_stats(new_members),
                "surging_activity": get_cohort_stats(surging_activity),
                "declining_activity": get_cohort_stats(declining_activity),
                "anomalous_behavior": get_cohort_stats(anomalous_behavior)
            },
            "cohorts": {
                # Original tabs you wanted to keep
                "new_members": new_members,
                "high_risk": high_risk_users,
                "recently_moderated": recently_moderated,
                "ai_flagged": ai_flagged_users,
                "power_users": power_users,
                # New behavioral tabs
                "surging_activity": surging_activity,
                "declining_activity": declining_activity,
                "anomalous_behavior": anomalous_behavior,
                # New social/community tabs
                "community_pillars": community_pillars,
                "isolated_members": isolated_members,
                "community_uplifters": community_uplifters,
                "chronic_critics": chronic_critics,
                "voice_vanguards": voice_vanguards,
                "returning_members": returning_members,
                # Other useful cohorts
                "lurkers": lurkers,
                "clean_record": clean_record_users,
            }
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))