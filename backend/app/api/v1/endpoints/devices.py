from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.sensor_device import SensorDevice
from app.db.session import get_db_session
from app.schemas.sensor_device import RegisterDeviceRequest, SensorDeviceResponse

router = APIRouter(tags=["devices"])


@router.post(
    "/devices/register",
    response_model=SensorDeviceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a Wokwi device for a field",
)
async def register_device(
    request: RegisterDeviceRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
):
    existing = await session.execute(
        select(SensorDevice).where(SensorDevice.device_id == request.device_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A device with this device_id is already registered",
        )

    device = SensorDevice(
        field_id=request.field_id,
        name=request.name,
        transport_type=request.transport_type,
        device_id=request.device_id,
        is_simulated=request.is_simulated,
    )
    session.add(device)
    await session.commit()
    await session.refresh(device)

    return SensorDeviceResponse(
        id=device.id,
        field_id=device.field_id,
        name=device.name,
        transport_type=device.transport_type,
        device_id=device.device_id,
        is_simulated=device.is_simulated,
        is_stale=device.is_stale,
        last_seen_at=device.last_seen_at,
        created_at=device.created_at,
    )
