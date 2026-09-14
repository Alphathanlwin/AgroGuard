from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.field import Field
from app.db.session import get_db_session
from app.schemas.demo import DemoResetRequest
from app.schemas.sensor_observation import IngestObservationRequest
from app.services.growth_sim import reset_demo_data
from app.services.observation import ingest_observation

router = APIRouter(tags=["demo"])


@router.get(
    "/demo-scenarios",
    status_code=status.HTTP_200_OK,
    summary="List available demo scenarios",
)
async def demo_scenarios():
    return [
        {"id": "healthy", "label": "Healthy baseline"},
        {"id": "dry-soil", "label": "Dry soil critical"},
        {"id": "heat-stress", "label": "Heat stress warning"},
    ]


@router.post(
    "/demo-scenarios/{scenario_id}/reset",
    status_code=status.HTTP_200_OK,
    summary="Reset a specific demo scenario",
)
async def reset_demo_scenario(
    scenario_id: str,
    session: Annotated[AsyncSession, Depends(get_db_session)] = None,
):
    if scenario_id not in {"healthy", "dry-soil", "heat-stress"}:
        raise HTTPException(status_code=404, detail="Demo scenario not found")
    return await _reset_demo(DemoResetRequest(scenario=scenario_id), session)


@router.post(
    "/demo/reset",
    status_code=status.HTTP_200_OK,
    summary="Full demo reset - clear and re-seed demo data",
)
async def reset_demo(
    data: DemoResetRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)] = None,
):
    return await _reset_demo(data, session)


async def _reset_demo(
    data: DemoResetRequest,
    session: AsyncSession,
) -> dict:
    field = await session.get(Field, 1)
    if not field:
        raise HTTPException(status_code=404, detail="Demo field not found")

    await reset_demo_data(session, field, data.scenario)

    if data.scenario == "dry-soil":
        await ingest_observation(
            session,
            IngestObservationRequest(
                event_id=f"demo-reset-dry-{uuid4().hex}",
                device_id=1,
                soil_moisture=12,
                temperature=30,
                humidity=68,
                ph=6.4,
                light=60,
            ),
        )
    elif data.scenario == "heat-stress":
        await ingest_observation(
            session,
            IngestObservationRequest(
                event_id=f"demo-reset-heat-{uuid4().hex}",
                device_id=1,
                soil_moisture=62,
                temperature=42,
                humidity=55,
                ph=6.4,
                light=75,
            ),
        )

    return {
        "scenarioId": data.scenario,
        "message": "Demo data cleared and re-seeded",
    }
