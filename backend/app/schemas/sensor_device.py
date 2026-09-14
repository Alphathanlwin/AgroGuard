from datetime import datetime

from app.schemas.base import APIModel


class RegisterDeviceRequest(APIModel):
    field_id: int
    name: str
    transport_type: str
    device_id: str
    is_simulated: bool = False


class SensorDeviceResponse(APIModel):
    id: int
    field_id: int
    name: str
    transport_type: str
    device_id: str
    is_simulated: bool
    is_stale: bool
    last_seen_at: datetime | None
    created_at: datetime
