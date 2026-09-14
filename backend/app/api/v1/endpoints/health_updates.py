from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.health_update import HealthUpdate
from app.db.session import get_db_session
from app.schemas.health_update import (
    HealthUpdateCreate,
    HealthUpdateResponse,
    HealthUpdateUpdate,
)

router = APIRouter(tags=["health-updates"])


@router.get(
    "/health-updates",
    response_model=list[HealthUpdateResponse],
    status_code=status.HTTP_200_OK,
    summary="List all health updates",
)
async def list_health_updates(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    result = await session.execute(
        select(HealthUpdate).order_by(HealthUpdate.reported_at.desc()).offset(skip).limit(limit)
    )
    return result.scalars().all()


@router.post(
    "/health-updates",
    response_model=HealthUpdateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new health update",
)
async def create_health_update(
    data: HealthUpdateCreate,
    session: Annotated[AsyncSession, Depends(get_db_session)],
):
    update = HealthUpdate(**data.model_dump())
    session.add(update)
    await session.commit()
    await session.refresh(update)
    return update


@router.get(
    "/health-updates/{update_id}",
    response_model=HealthUpdateResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a health update by ID",
)
async def get_health_update(
    update_id: int,
    session: Annotated[AsyncSession, Depends(get_db_session)],
):
    result = await session.execute(select(HealthUpdate).where(HealthUpdate.id == update_id))
    update = result.scalar_one_or_none()
    if not update:
        raise HTTPException(status_code=404, detail="Health update not found")
    return update


@router.put(
    "/health-updates/{update_id}",
    response_model=HealthUpdateResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a health update",
)
async def update_health_update(
    update_id: int,
    data: HealthUpdateUpdate,
    session: Annotated[AsyncSession, Depends(get_db_session)],
):
    result = await session.execute(select(HealthUpdate).where(HealthUpdate.id == update_id))
    update = result.scalar_one_or_none()
    if not update:
        raise HTTPException(status_code=404, detail="Health update not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(update, field, value)

    await session.commit()
    await session.refresh(update)
    return update


@router.delete(
    "/health-updates/{update_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a health update",
)
async def delete_health_update(
    update_id: int,
    session: Annotated[AsyncSession, Depends(get_db_session)],
):
    result = await session.execute(select(HealthUpdate).where(HealthUpdate.id == update_id))
    update = result.scalar_one_or_none()
    if not update:
        raise HTTPException(status_code=404, detail="Health update not found")

    await session.delete(update)
    await session.commit()
