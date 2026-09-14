from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.health_update import HealthUpdate
from app.db.session import get_db_session
from app.schemas.dashboard import (
    CropDistribution,
    DashboardResponse,
    OverviewStats,
    YieldByCrop,
)

router = APIRouter(tags=["dashboard"])


@router.get(
    "/dashboard/stats",
    response_model=DashboardResponse,
    status_code=status.HTTP_200_OK,
    summary="Get dashboard overview statistics",
)
async def get_dashboard_stats(session: Annotated[AsyncSession, Depends(get_db_session)]):
    total_records_result = await session.execute(select(func.count(HealthUpdate.id)))
    total_records = total_records_result.scalar() or 0

    return DashboardResponse(
        overview=OverviewStats(
            townships=112,
            records=total_records,
            yield_="3.6",
            rainfall="184",
        ),
        cropDistribution=[
            CropDistribution(crop="Rice", percent=42),
            CropDistribution(crop="Maize", percent=23),
            CropDistribution(crop="Pulses", percent=19),
            CropDistribution(crop="Sesame", percent=16),
        ],
        yieldByCrop=[
            YieldByCrop(crop="Rice", yield_=4.1),
            YieldByCrop(crop="Maize", yield_=3.2),
            YieldByCrop(crop="Pulses", yield_=2.6),
            YieldByCrop(crop="Sesame", yield_=1.9),
        ],
    )
