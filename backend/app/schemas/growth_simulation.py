from typing import Literal

from app.schemas.base import APIModel


class GrowthEventResponse(APIModel):
    event_date: str
    growth_stage: str
    health_index: int
    intervention: str | None = None
    risk_marker: str | None = None


class GrowthSimulationResponse(APIModel):
    id: int
    field_id: int
    crop_id: int
    scenario_type: str
    seed: str
    is_illustrative: bool
    events: list[GrowthEventResponse]


class GrowthStartRequest(APIModel):
    scenario: Literal["healthy", "dry-soil", "heat-stress"] = "healthy"
