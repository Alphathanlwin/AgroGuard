from datetime import datetime

from app.schemas.base import APIModel


class HealthUpdateCreate(APIModel):
    township: str
    crop_type: str
    health_status: str
    disease_details: str | None = None
    reported_by: str
    latitude: float | None = None
    longitude: float | None = None


class HealthUpdateUpdate(APIModel):
    township: str | None = None
    crop_type: str | None = None
    health_status: str | None = None
    disease_details: str | None = None
    reported_by: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class HealthUpdateResponse(APIModel):
    id: int
    township: str
    crop_type: str
    health_status: str
    disease_details: str | None = None
    reported_by: str
    latitude: float | None = None
    longitude: float | None = None
    reported_at: datetime
