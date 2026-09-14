from datetime import datetime

from app.schemas.base import APIModel


class IngestObservationRequest(APIModel):
    device_id: int
    event_id: str
    temperature: float | None = None
    humidity: float | None = None
    soil_moisture: float | None = None
    ph: float | None = None
    light: float | None = None
    recorded_at: datetime | None = None


class SimulateObservationRequest(APIModel):
    device_id: int
    scenario: str


class ObservationResponse(APIModel):
    id: int
    device_id: int
    event_id: str
    temperature: float | None
    humidity: float | None
    soil_moisture: float | None
    ph: float | None
    light: float | None
    recorded_at: datetime
