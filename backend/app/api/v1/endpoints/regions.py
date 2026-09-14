from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.region import Region
from app.db.session import get_db_session
from app.schemas.region import RegionResponse

router = APIRouter(tags=["regions"])


@router.get(
    "/regions",
    response_model=list[RegionResponse],
    status_code=status.HTTP_200_OK,
    summary="List all Myanmar regions",
)
async def list_regions(session: Annotated[AsyncSession, Depends(get_db_session)]):
    result = await session.execute(select(Region).order_by(Region.name_en))
    return result.scalars().all()
