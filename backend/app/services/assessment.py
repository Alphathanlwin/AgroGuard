from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.assessment import Assessment
from app.db.models.crop_profile import CropProfile
from app.db.models.crop_requirement import CropRequirement
from app.db.models.field import Field
from app.db.models.field_context_snapshot import FieldContextSnapshot
from app.db.models.sensor_device import SensorDevice
from app.db.models.sensor_observation import SensorObservation
from app.db.session import utcnow
from app.services.alerting import create_alert_for_assessment

_CRITICALITY_WEIGHTS = {
    "critical": 3.0,
    "important": 1.5,
    "advisory": 0.5,
}


def _compute_factor_impact(
    value: float | None,
    req_min: float,
    req_max: float,
    criticality: str,
) -> dict:
    if value is None:
        return {
            "impact": 0.0,
            "status": "unknown",
            "gap": None,
        }

    if req_min <= value <= req_max:
        return {"impact": 0.0, "status": "within_range", "gap": 0.0}
    elif value < req_min:
        gap = (req_min - value) / max(abs(req_min), 0.001)
        impact = min(gap * _CRITICALITY_WEIGHTS.get(criticality, 1.0), 20.0)
        return {"impact": round(impact, 2), "status": "below_range", "gap": round(gap, 3)}
    else:
        gap = (value - req_max) / max(abs(req_max), 0.001)
        impact = min(gap * _CRITICALITY_WEIGHTS.get(criticality, 1.0), 20.0)
        return {"impact": round(impact, 2), "status": "above_range", "gap": round(gap, 3)}


def run_assessment(
    observation: SensorObservation,
    context: FieldContextSnapshot | None,
    requirements: list[CropRequirement],
) -> dict:
    field_values = {}

    for key in ("temperature", "humidity", "soil_moisture", "ph", "light"):
        obs_val = getattr(observation, key, None)
        ctx_val = getattr(context, key, None) if context else None
        field_values[key] = obs_val if obs_val is not None else ctx_val

    field_values["rainfall"] = context.rainfall if context else None

    evidence_list = []
    total_impact = 0.0

    for req in requirements:
        value = field_values.get(req.factor)
        result = _compute_factor_impact(value, req.min_value, req.max_value, req.criticality)
        factor_entry = {
            "factor": req.factor,
            "value": value,
            "range_min": req.min_value,
            "range_max": req.max_value,
            "unit": req.unit,
            "criticality": req.criticality,
            "impact": result["impact"],
            "status": result["status"],
        }
        evidence_list.append(factor_entry)
        total_impact += result["impact"]

    health_score = max(0.0, 100.0 - total_impact)

    if health_score >= 70:
        status = "healthy"
    elif health_score >= 40:
        status = "warning"
    else:
        status = "critical"

    risk_factors = [
        f"{e['factor']}_{e['status']}"
        for e in evidence_list
        if e["status"] in ("below_range", "above_range") and e["criticality"] != "advisory"
    ]
    primary_risk = risk_factors[0] if risk_factors else None

    recommendation = _generate_recommendation(primary_risk, health_score, status)

    decision_mode = "rules"

    confidence = "high"
    if any(e.get("status") == "unknown" for e in evidence_list):
        confidence = "medium"

    return {
        "status": status,
        "health_score": round(health_score, 1),
        "primary_risk": primary_risk,
        "recommendation": recommendation,
        "evidence": {"factors": evidence_list, "total_impact": round(total_impact, 1)},
        "confidence": confidence,
        "decision_mode": decision_mode,
    }


def _generate_recommendation(
    primary_risk: str | None,
    health_score: float,
    status: str,
) -> str:
    if status == "healthy":
        return "Conditions are within the crop profile. Continue routine monitoring."

    if primary_risk:
        if "temperature" in primary_risk:
            return "Adjust planting schedule or select a heat/cold-tolerant variety."
        if "soil_moisture" in primary_risk:
            return "Irrigate to raise soil moisture to the target range."
        if "ph" in primary_risk:
            return "Apply lime or sulfur to adjust pH to the target range."
        if "light" in primary_risk:
            return "Use shade management or select a variety suited to local light conditions."
        if "rainfall" in primary_risk:
            return "Plan supplemental irrigation or drainage based on expected rainfall."
        if "humidity" in primary_risk:
            return "Monitor for disease; consider ventilation or spacing adjustments."
        return "Address the most critical out-of-range factor first."

    return "Review field conditions and crop requirements for optimal management."


async def recompute_assessment(
    session: AsyncSession,
    field: Field,
) -> tuple[Assessment, Any, Any]:
    crop_result = await session.execute(
        select(CropProfile).options(selectinload(CropProfile.requirements)).limit(1)
    )
    crop_profile = crop_result.scalar_one_or_none()
    if not crop_profile:
        raise ValueError("No crop profile found")

    obs_result = await session.execute(
        select(SensorObservation)
        .join(SensorDevice, SensorDevice.id == SensorObservation.device_id)
        .where(SensorDevice.field_id == field.id)
        .order_by(SensorObservation.id.desc())
        .limit(1)
    )
    observation = obs_result.scalar_one_or_none()

    ctx_result = await session.execute(
        select(FieldContextSnapshot)
        .where(FieldContextSnapshot.field_id == field.id)
        .order_by(FieldContextSnapshot.captured_at.desc())
        .limit(1)
    )
    context = ctx_result.scalar_one_or_none()

    result = run_assessment(observation, context, crop_profile.requirements)
    confidence = "high"
    if any(e.get("status") == "unknown" for e in result.get("evidence", {}).get("factors", [])):
        confidence = "medium"

    assessment = Assessment(
        field_id=field.id,
        observation_id=observation.id if observation else None,
        crop_profile_id=crop_profile.id,
        status=result["status"],
        health_score=result["health_score"],
        primary_risk=result["primary_risk"],
        recommendation=result["recommendation"],
        evidence=result["evidence"],
        confidence=confidence,
        decision_mode=result["decision_mode"],
        updated_at=utcnow(),
    )
    session.add(assessment)
    await session.flush()

    alert, delivery = await create_alert_for_assessment(session, field=field, assessment=assessment)
    await session.commit()
    await session.refresh(assessment)
    return assessment, alert, delivery
