from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.field import Field
from app.db.models.growth_simulation_event import GrowthEvent
from app.db.session import get_db_session
from app.schemas.growth_simulation import (
    GrowthEventResponse,
    GrowthSimulationResponse,
    GrowthStartRequest,
)
from app.services.growth_sim import ensure_simulations, start_growth_replay

router = APIRouter(tags=["simulations"])


async def _build_simulation_response(
    session: AsyncSession, field_id: int
) -> list[dict]:
    simulations = await ensure_simulations(session, field_id, 1)
    result = []
    for sim in simulations:
        events_result = await session.execute(
            select(GrowthEvent)
            .where(GrowthEvent.simulation_id == sim.id)
            .order_by(GrowthEvent.event_date)
        )
        events = events_result.scalars().all()
        result.append({
            "id": sim.id,
            "field_id": sim.field_id,
            "crop_id": sim.crop_profile_id,
            "scenario_type": sim.scenario_type,
            "seed": sim.seed,
            "is_illustrative": sim.is_illustrative,
            "events": [GrowthEventResponse(
                event_date=e.event_date,
                growth_stage=e.growth_stage,
                health_index=e.health_index,
                intervention=e.intervention,
                risk_marker=e.risk_marker,
            ) for e in events],
        })
    return result


@router.get(
    "/fields/{field_id}/growth-simulations",
    response_model=list[GrowthSimulationResponse],
    status_code=status.HTTP_200_OK,
    summary="List growth simulations for a field",
)
async def list_simulations(
    field_id: int,
    session: Annotated[AsyncSession, Depends(get_db_session)] = None,
):
    return await _build_simulation_response(session, field_id)


@router.post(
    "/fields/{field_id}/growth-simulations/replay",
    response_model=list[GrowthSimulationResponse],
    status_code=status.HTTP_200_OK,
    summary="Replay growth simulations",
)
async def replay_simulations(
    field_id: int,
    session: Annotated[AsyncSession, Depends(get_db_session)] = None,
):
    return await _build_simulation_response(session, field_id)


@router.post(
    "/fields/{field_id}/growth/start",
    response_model=list[GrowthSimulationResponse],
    status_code=status.HTTP_200_OK,
    summary="Start a growth replay with a scenario",
)
async def start_growth(
    field_id: int,
    data: GrowthStartRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)] = None,
):
    field = await session.get(Field, field_id)
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    await start_growth_replay(session, field, data.scenario)
    return await _build_simulation_response(session, field_id)


@router.get(
    "/fields/{field_id}/growth/timeline",
    response_model=list[GrowthSimulationResponse],
    status_code=status.HTTP_200_OK,
    summary="Get growth timeline for a field",
)
async def growth_timeline(
    field_id: int,
    session: Annotated[AsyncSession, Depends(get_db_session)] = None,
):
    return await _build_simulation_response(session, field_id)
