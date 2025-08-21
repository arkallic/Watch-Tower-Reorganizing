# api/endpoints/spotlight.py
from fastapi import APIRouter, HTTPException, Request
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel

router = APIRouter(prefix="/spotlight", tags=["spotlight"])

# Global dependencies
bot = None
bot_settings = None

def initialize_dependencies(bot_instance, bot_settings_instance):
    global bot, bot_settings
    bot = bot_instance
    bot_settings = bot_settings_instance

class VerificationPayload(BaseModel):
    userId: str
    key: str
    answers: Dict[str, str]
    recaptchaResponse: Optional[str] = None
    ip: Optional[str] = None

class LogPayload(BaseModel):
    userId: str
    username: str
    display_name: str
    avatar: str
    status: str
    date: str
    time_to_complete: float
    captcha_fails: int
    failed_questions: List[str]
    red_flags: List[str]
    score: int
    total_questions: int
    passed: bool

class ManualDecisionPayload(BaseModel):
    userId: str
    decision: str  # "approve" or "reject"
    moderatorId: Optional[str] = None

def load_spotlight_data():
    """Helper function to load spotlight log data."""
    log_file = Path("spotlight_log.json")
    if not log_file.exists():
        with log_file.open('w', encoding='utf-8') as f:
            json.dump([], f)
        return []
    with log_file.open('r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

async def check_ip_abuse(ip_address: str, settings: dict):
    """Check IP against abuse databases if enabled."""
    results = {}
    
    if not ip_address:
        return results
        
    try:
        # IP API check
        if settings.get("ip_check_enabled"):
            results['ip_api'] = "Clean (Simulated)"
            
        # StopForumSpam check  
        if settings.get("stopforumspam_enabled"):
            results['stop_forum_spam'] = "Clean (Simulated)"
            
        # AbuseIPDB check
        if settings.get("abuseipdb_enabled"):
            results['abuse_ip_db'] = "Clean (Simulated)"
            
    except Exception as e:
        results['error'] = str(e)
        
    return results

@router.get("/config/{user_id}/{key}")
async def get_spotlight_config(user_id: str, key: str):
    """Get spotlight configuration for user verification"""
    try:
        # Validate key
        if not hasattr(bot, 'spotlight_tokens') or user_id not in bot.spotlight_tokens:
            return {"error": "Invalid or expired verification link"}
            
        token_data = bot.spotlight_tokens[user_id]
        if token_data["token"] != key or token_data["used"]:
            return {"error": "Invalid or expired verification link"}
            
        if datetime.now() > token_data["expires"]:
            return {"error": "Verification link has expired"}
            
        spotlight_settings = bot_settings.get("spotlight", {})
        
        # Return configuration
        return {
            "success": True,
            "rules": spotlight_settings.get("rules_content", ""),
            "questions": spotlight_settings.get("questions", []),
            "recaptcha_site_key": spotlight_settings.get("recaptcha_site_key", ""),
            "captcha_enabled": spotlight_settings.get("captcha_enabled", True),
            "passing_score": spotlight_settings.get("passing_score", 3)
        }
        
    except Exception as e:
        return {"error": str(e)}

@router.post("/verify")
async def verify_spotlight_submission(payload: VerificationPayload):
    """Process spotlight verification submission"""
    try:
        user_id = payload.userId
        key = payload.key
        answers = payload.answers
        recaptcha_response = payload.recaptchaResponse
        ip_address = payload.ip
        
        # Validate key
        if not hasattr(bot, 'spotlight_tokens') or user_id not in bot.spotlight_tokens:
            return {"success": False, "error": "Invalid verification"}
            
        token_data = bot.spotlight_tokens[user_id]
        if token_data["token"] != key or token_data["used"]:
            return {"success": False, "error": "Invalid or expired verification"}
            
        if datetime.now() > token_data["expires"]:
            return {"success": False, "error": "Verification expired"}
            
        spotlight_settings = bot_settings.get("spotlight", {})
        
        # Verify reCAPTCHA if enabled
        if spotlight_settings.get("captcha_enabled") and recaptcha_response:
            recaptcha_secret = spotlight_settings.get("recaptcha_secret_key")
            if recaptcha_secret:
                try:
                    import requests
                    recaptcha_data = {
                        'secret': recaptcha_secret,
                        'response': recaptcha_response
                    }
                    recaptcha_result = requests.post(
                        'https://www.google.com/recaptcha/api/siteverify',
                        data=recaptcha_data,
                        timeout=10
                    )
                    if not recaptcha_result.json().get('success'):
                        return {"success": False, "error": "reCAPTCHA verification failed"}
                except Exception as e:
                    return {"success": False, "error": "reCAPTCHA verification error"}
        
        # Check answers
        questions = spotlight_settings.get("questions", [])
        correct_answers = 0
        total_questions = len(questions)
        failed_questions = []
        
        for question in questions:
            user_answer = answers.get(question["id"])
            if user_answer == question["correct_answer"]:
                correct_answers += 1
            else:
                failed_questions.append(question["text"])
                
        passing_score = spotlight_settings.get("passing_score", 3)
        passed = correct_answers >= passing_score
        
        # Security checks
        security_flags = []
        abuse_results = await check_ip_abuse(ip_address, spotlight_settings)
        
        if abuse_results:
            for check, result in abuse_results.items():
                if "error" in result.lower() or "flagged" in result.lower():
                    security_flags.append(f"IP {check}: {result}")
        
        # Mark token as used
        bot.spotlight_tokens[user_id]["used"] = True
        
        result = {
            "success": True,
            "passed": passed,
            "score": correct_answers,
            "total": total_questions,
            "required": passing_score,
            "failed_questions": failed_questions,
            "security_flags": security_flags,
            "abuse_checks": abuse_results,
            "requires_manual_review": len(security_flags) > 0 or not passed
        }
        
        return result
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.post("/log")
async def log_spotlight_attempt(payload: LogPayload):
    """Log spotlight verification attempt"""
    try:
        # Get member for red flag calculation
        guild = bot.guilds[0] if bot.guilds else None
        red_flags = []
        
        if guild:
            try:
                member = guild.get_member(int(payload.userId))
                if member:
                    # Account age check
                    account_age = datetime.now(datetime.timezone.utc) - member.created_at
                    if account_age.total_seconds() < (48 * 3600):  # Less than 48 hours
                        red_flags.append("Account created less than 48 hours ago")
                        
                    # Default avatar check
                    if member.avatar is None:
                        red_flags.append("Using default Discord avatar")
            except Exception:
                pass
        
        # Load existing log
        all_logs = load_spotlight_data()
        
        # Create log entry
        log_entry = payload.dict()
        log_entry["red_flags"] = red_flags
        log_entry["timestamp"] = datetime.now().isoformat()
        
        # Append to log
        all_logs.append(log_entry)
        
        # Keep only last 1000 entries
        if len(all_logs) > 1000:
            all_logs = all_logs[-1000:]
            
        # Save log
        with open("spotlight_log.json", 'w', encoding='utf-8') as f:
            json.dump(all_logs, f, indent=2)
            
        return {"success": True}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/summary")
async def get_spotlight_summary():
    """Get spotlight analytics summary"""
    try:
        data = load_spotlight_data()
        
        if not data:
            return {
                "total_screened": 0,
                "pass_rate": 0,
                "pending_review": 0,
                "total_captcha_fails": 0,
                "avg_completion_time": 0,
                "top_failed_questions": [],
                "outcome_breakdown": []
            }

        total_screened = len(data)
        passed_count = len([u for u in data if u.get('status') in ['Passed', 'Manually Approved']])
        pending_review = len([u for u in data if u.get('status') == 'Pending'])
        total_captcha_fails = sum(u.get('captcha_fails', 0) for u in data)

        # Calculate average completion time
        completion_times = [u.get('time_to_complete', 0) for u in data if u.get('status') == 'Passed' and u.get('time_to_complete')]
        avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0

        # Top failed questions
        failed_questions = {}
        for user in data:
            if user.get('failed_questions'):
                for q in user['failed_questions']:
                    failed_questions[q] = failed_questions.get(q, 0) + 1
        top_failed_questions = [
            {"name": q, "fails": c} 
            for q, c in sorted(failed_questions.items(), key=lambda item: item[1], reverse=True)[:5]
        ]

        # Outcome breakdown
        outcome_breakdown = {"Passed": 0, "Pending": 0, "Rejected": 0, "Manually Approved": 0}
        for item in data:
            status = item.get('status', 'Unknown')
            if status in outcome_breakdown:
                outcome_breakdown[status] += 1

        return {
            "total_screened": total_screened,
            "pass_rate": round((passed_count / total_screened) * 100, 1) if total_screened > 0 else 0,
            "pending_review": pending_review,
            "total_captcha_fails": total_captcha_fails,
            "avg_completion_time": round(avg_completion_time, 2),
            "top_failed_questions": top_failed_questions,
            "outcome_breakdown": [{"name": k, "value": v} for k, v in outcome_breakdown.items() if v > 0]
        }
        
    except Exception as e:
        return {"error": str(e)}

@router.get("/history")
async def get_spotlight_history():
    """Get full spotlight verification history"""
    try:
        data = load_spotlight_data()
        # Sort by date/timestamp (newest first)
        sorted_data = sorted(
            data, 
            key=lambda x: x.get('timestamp', x.get('date', '')), 
            reverse=True
        )
        return {"history": sorted_data}
        
    except Exception as e:
        return {"error": str(e)}

@router.post("/manual-decision")
async def handle_manual_decision(payload: ManualDecisionPayload):
    """Handle manual moderator decision for spotlight verification"""
    try:
        user_id = int(payload.userId)
        decision = payload.decision
        
        guild = bot.guilds[0] if bot.guilds else None
        if not guild:
            return {"success": False, "error": "No guild available"}
            
        member = guild.get_member(user_id)
        if not member:
            return {"success": False, "error": "Member not found"}
            
        spotlight_settings = bot_settings.get("spotlight", {})
        
        # Update log entry
        all_logs = load_spotlight_data()
        log_updated = False
        
        for log in all_logs:
            if log.get('userId') == str(user_id) or log.get('user_id') == user_id:
                if log.get('status') == 'Pending':
                    if decision == "approve":
                        # Grant verified role
                        verified_role_id = spotlight_settings.get("verified_role_id")
                        if verified_role_id:
                            role = guild.get_role(int(verified_role_id))
                            if role:
                                await member.add_roles(role, reason="Spotlight verification approved")
                        
                        log['status'] = "Manually Approved"
                        
                        # Delete private channel
                        if hasattr(bot, 'spotlight_tokens') and str(user_id) in bot.spotlight_tokens:
                            channel_id = bot.spotlight_tokens[str(user_id)].get("channel_id")
                            if channel_id:
                                channel = guild.get_channel(channel_id)
                                if channel:
                                    await channel.delete(reason="Verification completed")
                            # Clean up token
                            del bot.spotlight_tokens[str(user_id)]
                            
                    elif decision == "reject":
                        log['status'] = "Rejected"
                        
                        # Delete private channel and kick user
                        if hasattr(bot, 'spotlight_tokens') and str(user_id) in bot.spotlight_tokens:
                            channel_id = bot.spotlight_tokens[str(user_id)].get("channel_id")
                            if channel_id:
                                channel = guild.get_channel(channel_id)
                                if channel:
                                    await channel.delete(reason="Verification rejected")
                            # Clean up token
                            del bot.spotlight_tokens[str(user_id)]
                            
                        await member.kick(reason="Failed verification process")
                        
                    log_updated = True
                    break
        
        if log_updated:
            with open("spotlight_log.json", 'w', encoding='utf-8') as f:
                json.dump(all_logs, f, indent=2)
            return {"success": True, "message": f"Action '{decision}' completed for {member.display_name}"}
        else:
            return {"success": False, "error": "No pending verification found for this user"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}