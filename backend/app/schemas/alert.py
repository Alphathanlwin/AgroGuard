from datetime import datetime

from app.schemas.base import APIModel


class AlertResponse(APIModel):
    id: int
    field_id: int
    assessment_id: int
    fingerprint: str
    severity: str
    risk_type: str
    message: str
    status: str
    opened_at: datetime
    acknowledged_at: datetime | None = None
    resolved_at: datetime | None = None


class NotificationResponse(APIModel):
    id: int
    alert_id: int
    channel: str
    destination_ref: str
    delivery_key: str
    status: str
    attempt_count: int
    last_error_code: str | None = None
    sent_at: datetime | None = None
