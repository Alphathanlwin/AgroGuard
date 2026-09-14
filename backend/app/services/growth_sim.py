from datetime import UTC, date, datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.alert import Alert
from app.db.models.assessment import Assessment
from app.db.models.field import Field
from app.db.models.growth_simulation import GrowthSimulation
from app.db.models.growth_simulation_event import GrowthEvent
from app.db.models.notification_delivery import Notification
from app.db.models.sensor_device import SensorDevice
from app.db.models.sensor_observation import SensorObservation

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
STAGES = [
    "Germination", "Germination",
    "Vegetative", "Vegetative",
    "Flowering", "Flowering",
    "Fruiting", "Fruiting",
    "Grain filling", "Grain filling",
    "Harvest", "Harvest",
]


async def _build_scenario(
    session: AsyncSession, *,
    field_id: int, crop_profile_id: int,
    scenario_type: str, seed: str, stressed: bool,
) -> GrowthSimulation:
    simulation = GrowthSimulation(
        field_id=field_id,
        crop_profile_id=crop_profile_id,
        scenario_type=scenario_type,
        seed=seed,
        is_illustrative=True,
    )
    session.add(simulation)
    await session.flush()

    year = datetime.now(UTC).year
    for index, (_month, stage) in enumerate(zip(MONTHS, STAGES, strict=True)):
        recovery = 10 if scenario_type == "iot_guided" and stressed and index >= 3 else 0
        degradation = 3 * max(0, index - 2) if scenario_type == "normal_control" and stressed else 0
        health = max(25, min(98, 86 - (12 if stressed else 0) + recovery - degradation))
        session.add(GrowthEvent(
            simulation_id=simulation.id,
            event_date=str(date(year, index + 1, 15)),
            growth_stage=stage,
            health_index=health,
            intervention="Irrigation alert acted on; moisture recovered." if recovery else None,
            risk_marker=(
                "dry-soil" if stressed and index == 2
                else "heat-stress" if stressed and index == 3
                else None
            ),
        ))
    return simulation


async def start_growth_replay(
    session: AsyncSession,
    field: Field,
    scenario: str = "healthy",
) -> list[GrowthSimulation]:
    sims = await session.execute(
        select(GrowthSimulation).where(GrowthSimulation.field_id == field.id)
    )
    for sim in sims.scalars().all():
        await session.execute(
            delete(GrowthEvent).where(GrowthEvent.simulation_id == sim.id)
        )
    await session.execute(
        delete(GrowthSimulation).where(GrowthSimulation.field_id == field.id)
    )

    stressed = scenario != "healthy"
    crop_profile_id = getattr(field, "selected_crop_id", None) or 1
    if isinstance(crop_profile_id, str):
        crop_profile_id = 1

    s1 = await _build_scenario(
        session, field_id=field.id, crop_profile_id=crop_profile_id,
        scenario_type="iot_guided", seed=f"{scenario}-guided-v2", stressed=stressed,
    )
    s2 = await _build_scenario(
        session, field_id=field.id, crop_profile_id=crop_profile_id,
        scenario_type="normal_control", seed=f"{scenario}-control-v2", stressed=stressed,
    )
    await session.commit()
    return [s1, s2]


async def ensure_simulations(
    session: AsyncSession,
    field_id: int,
    crop_profile_id: int,
) -> list[GrowthSimulation]:
    result = await session.execute(
        select(GrowthSimulation).where(GrowthSimulation.field_id == field_id)
    )
    existing = list(result.scalars().all())
    if existing:
        return existing
    field = await session.get(Field, field_id)
    if not field:
        return []
    return await start_growth_replay(session, field, "healthy")


async def reset_demo_data(
    session: AsyncSession,
    field: Field,
    scenario: str = "healthy",
) -> list[GrowthSimulation]:
    sims = await session.execute(
        select(GrowthSimulation).where(GrowthSimulation.field_id == field.id)
    )
    for sim in sims.scalars().all():
        await session.execute(
            delete(GrowthEvent).where(GrowthEvent.simulation_id == sim.id)
        )
    await session.execute(
        delete(GrowthSimulation).where(GrowthSimulation.field_id == field.id)
    )

    alert_result = await session.execute(select(Alert).where(Alert.field_id == field.id))
    for alert in alert_result.scalars().all():
        await session.execute(delete(Notification).where(Notification.alert_id == alert.id))
    await session.execute(delete(Alert).where(Alert.field_id == field.id))
    await session.execute(delete(Assessment).where(Assessment.field_id == field.id))
    dev_result = await session.execute(
        select(SensorDevice).where(SensorDevice.field_id == field.id)
    )
    device_ids = [d.id for d in dev_result.scalars().all()]
    if device_ids:
        await session.execute(
            delete(SensorObservation).where(SensorObservation.device_id.in_(device_ids))
        )

    await session.commit()
    return await start_growth_replay(session, field, scenario)
