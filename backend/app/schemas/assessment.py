from datetime import datetime

from app.schemas.base import APIModel


class AssessmentResponse(APIModel):
    id: int
    field_id: int
    observation_id: int | None
    crop_profile_id: int | None
    status: str
    health_score: float
    primary_risk: str | None
    recommendation: str | None
    evidence: dict | None
    decision_mode: str
    created_at: datetime


class FieldStatusResponse(APIModel):
    field_id: int
    latest_assessment: AssessmentResponse | None
    device_count: int
    active_devices: int
    stale_devices: int
