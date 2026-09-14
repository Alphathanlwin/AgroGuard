from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.field import Field
from app.db.models.sensor_device import SensorDevice
from app.db.models.sensor_observation import SensorObservation
from app.schemas.sensor_observation import IngestObservationRequest, ObservationResponse
from app.services.assessment import recompute_assessment

_PLAUSIBLE_RANGES = {
    "temperature": (-10.0, 60.0),
    "humidity": (0.0, 100.0),
    "soil_moisture": (0.0, 100.0),
    "ph": (0.0, 14.0),
    "light": (0.0, 100.0),
}

_SCENARIO_VALUES = {
    "dry_soil": {
        "temperature": 32.0,
        "humidity": 45.0,
        "soil_moisture": 15.0,
        "ph": 6.5,
        "light": 90.0,
    },
    "heat_stress": {
        "temperature": 42.0,
        "humidity": 30.0,
        "soil_moisture": 30.0,
        "ph": 6.8,
        "light": 95.0,
    },
    "ideal": {
        "temperature": 26.0,
        "humidity": 65.0,
        "soil_moisture": 60.0,
        "ph": 6.5,
        "light": 75.0,
    },
    "waterlogged": {
        "temperature": 28.0,
        "humidity": 85.0,
        "soil_moisture": 95.0,
        "ph": 5.8,
        "light": 50.0,
    },
    "cold_snap": {
        "temperature": 8.0,
        "humidity": 75.0,
        "soil_moisture": 70.0,
        "ph": 6.2,
        "light": 40.0,
    },
}


def validate_reading(field: str, value: float | None) -> float | None:
    if value is None:
        return None
    lo, hi = _PLAUSIBLE_RANGES[field]
    if not (lo <= value <= hi):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{field} value {value} is outside plausible range [{lo}, {hi}]",
        )
    return value


def validate_observation(payload: IngestObservationRequest) -> None:
    for field in ("temperature", "humidity", "soil_moisture", "ph", "light"):
        validate_reading(field, getattr(payload, field))


async def ingest_observation(
    session: AsyncSession,
    payload: IngestObservationRequest,
) -> ObservationResponse:
    device = await session.get(SensorDevice, payload.device_id)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")

    existing = await session.execute(
        select(SensorObservation).where(SensorObservation.event_id == payload.event_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Observation with event_id '{payload.event_id}' already exists",
        )

    validate_observation(payload)

    observation = SensorObservation(
        device_id=payload.device_id,
        event_id=payload.event_id,
        temperature=payload.temperature,
        humidity=payload.humidity,
        soil_moisture=payload.soil_moisture,
        ph=payload.ph,
        light=payload.light,
        recorded_at=payload.recorded_at or datetime.now(UTC),
    )
    session.add(observation)
    device.last_seen_at = datetime.now(UTC)
    device.is_stale = False

    await session.commit()
    await session.refresh(observation)

    field = await session.get(Field, device.field_id)
    if field:
        await recompute_assessment(session, field)

    return ObservationResponse(
        id=observation.id,
        device_id=observation.device_id,
        event_id=observation.event_id,
        temperature=observation.temperature,
        humidity=observation.humidity,
        soil_moisture=observation.soil_moisture,
        ph=observation.ph,
        light=observation.light,
        recorded_at=observation.recorded_at,
    )


def simulate_scenario(device: SensorDevice, scenario: str) -> IngestObservationRequest:
    values = _SCENARIO_VALUES.get(scenario)
    if not values:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown scenario '{scenario}'. Choose from: {list(_SCENARIO_VALUES.keys())}",
        )
    return IngestObservationRequest(
        device_id=device.id,
        event_id=f"sim_{scenario}_{datetime.now(UTC).isoformat()}",
        **values,
    )


async def check_stale(device: SensorDevice) -> bool:
    if device.last_seen_at is None:
        return False
    stale_threshold = datetime.now(UTC).replace(tzinfo=None) - timedelta(minutes=30)
    last_seen = device.last_seen_at.replace(tzinfo=None)
    return last_seen < stale_threshold
