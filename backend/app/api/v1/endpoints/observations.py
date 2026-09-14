from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.sensor_device import SensorDevice
from app.db.session import get_db_session
from app.schemas.sensor_observation import (
    IngestObservationRequest,
    ObservationResponse,
    SimulateObservationRequest,
)
from app.services.observation import ingest_observation as save_observation
from app.services.observation import simulate_scenario

router = APIRouter(tags=["observations"])


@router.post(
    "/observations/ingest",
    response_model=ObservationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Accept normalized sensor readings from a device",
)
async def ingest_observation(
    request: IngestObservationRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
):
    return await save_observation(session, request)


@router.post(
    "/observations/simulate",
    response_model=ObservationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a simulated observation for manual scenario testing",
)
async def simulate_observation(
    request: SimulateObservationRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
):
    device = await session.get(SensorDevice, request.device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    simulated = simulate_scenario(device, request.scenario)
    return await save_observation(session, simulated)
