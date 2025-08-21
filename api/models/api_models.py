# api/models/api_models.py
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional

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

class ReportRequest(BaseModel):
    report_type: str = Field(default="moderation_summary")
    time_range: str = Field(default="30d")

class CaseActionRequest(BaseModel):
    action_type: str
    reason: str
    severity: str = Field(default="Medium")
    duration: Optional[int] = None
    send_dm: bool = Field(default=True)