from datetime import datetime

from app.schemas.base import APIModel


class FieldResponse(APIModel):
    id: int
    name: str
    latitude: float
    longitude: float
    region_code: str | None
    created_at: datetime


class SelectFieldRequest(APIModel):
    field_id: int


class FieldContextResponse(APIModel):
    soil_moisture: float | None
    ph: float | None
    temperature: float | None
    humidity: float | None
    light: float | None
    rainfall: float | None
    captured_at: datetime | None


class SelectFieldResponse(APIModel):
    field: FieldResponse
    context: FieldContextResponse | None
    available_crops: list[str]
