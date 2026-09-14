from app.db.models.crop_profile import CropProfile
from app.db.models.crop_requirement import CropRequirement
from app.db.models.field_context_snapshot import FieldContextSnapshot
from app.schemas.crop_profile import CropSuitabilityResponse, FactorEvidence

_CRITICALITY_WEIGHTS = {
    "critical": 3.0,
    "important": 1.5,
    "advisory": 0.5,
}


def _compute_factor_impact(
    value: float | None,
    req: CropRequirement,
) -> FactorEvidence:
    if value is None:
        return FactorEvidence(
            factor=req.factor,
            value=None,
            range_min=req.min_value,
            range_max=req.max_value,
            unit=req.unit,
            impact=0.0,
            criticality=req.criticality,
            status="unknown",
        )

    if req.min_value <= value <= req.max_value:
        impact = 0.0
        status = "within_range"
    elif value < req.min_value:
        gap = (req.min_value - value) / max(abs(req.min_value), 0.001)
        impact = min(gap * _CRITICALITY_WEIGHTS.get(req.criticality, 1.0), 20.0)
        status = "below_range"
    else:
        gap = (value - req.max_value) / max(abs(req.max_value), 0.001)
        impact = min(gap * _CRITICALITY_WEIGHTS.get(req.criticality, 1.0), 20.0)
        status = "above_range"

    return FactorEvidence(
        factor=req.factor,
        value=value,
        range_min=req.min_value,
        range_max=req.max_value,
        unit=req.unit,
        impact=impact,
        criticality=req.criticality,
        status=status,
    )


def score_suitability(
    crop_profile: CropProfile,
    requirements: list[CropRequirement],
    context: FieldContextSnapshot | None,
) -> CropSuitabilityResponse:
    field_values = {
        "temperature": context.temperature if context else None,
        "humidity": context.humidity if context else None,
        "soil_moisture": context.soil_moisture if context else None,
        "ph": context.ph if context else None,
        "light": context.light if context else None,
        "rainfall": context.rainfall if context else None,
    }

    evidence = [_compute_factor_impact(field_values.get(r.factor), r) for r in requirements]

    total_impact = sum(e.impact for e in evidence)
    score = max(0.0, 100.0 - total_impact)

    risk_factors = [
        f"{e.factor}_{e.status}"
        for e in evidence
        if e.status in ("below_range", "above_range") and e.criticality != "advisory"
    ]

    primary_risk = risk_factors[0] if risk_factors else None
    if primary_risk:
        if "temperature" in primary_risk:
            recommendation = "Adjust planting schedule or select a heat/cold-tolerant variety."
        elif "soil_moisture" in primary_risk:
            recommendation = "Irrigate to raise soil moisture to the target range."
        elif "ph" in primary_risk:
            recommendation = "Apply lime or sulfur to adjust pH to the target range."
        elif "light" in primary_risk:
            recommendation = "Use shade management or select a variety suited to local light."
        elif "rainfall" in primary_risk:
            recommendation = "Plan supplemental irrigation or drainage based on expected rainfall."
        elif "humidity" in primary_risk:
            recommendation = "Monitor for disease; consider ventilation or spacing adjustments."
        else:
            recommendation = "Address the most critical out-of-range factor first."
    else:
        recommendation = "Field conditions are within the crop's optimal range."

    return CropSuitabilityResponse(
        score=round(score, 1),
        risk_factors=risk_factors,
        recommendation=recommendation,
        evidence=evidence,
    )
