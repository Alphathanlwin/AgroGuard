
from app.schemas.base import APIModel


class CropRequirementResponse(APIModel):
    id: int
    factor: str
    min_value: float
    max_value: float
    unit: str
    criticality: str


class CropProfileResponse(APIModel):
    id: int
    name: str
    description: str | None
    source: str | None
    requirements: list[CropRequirementResponse]


class CropSuitabilityRequest(APIModel):
    field_id: int
    crop_profile_id: int


class FactorEvidence(APIModel):
    factor: str
    value: float | None
    range_min: float
    range_max: float
    unit: str
    impact: float
    criticality: str
    status: str


class CropSuitabilityResponse(APIModel):
    score: float
    risk_factors: list[str]
    recommendation: str
    evidence: list[FactorEvidence]
