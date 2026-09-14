from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.crop_profile import CropProfile
from app.db.session import get_db_session
from app.schemas.crop_profile import CropProfileResponse, CropRequirementResponse

router = APIRouter(tags=["crop-profiles"])


@router.get(
    "/crop-profiles",
    response_model=list[CropProfileResponse],
    status_code=status.HTTP_200_OK,
    summary="List crop profiles with their requirements",
)
async def list_crop_profiles(session: Annotated[AsyncSession, Depends(get_db_session)]):
    result = await session.execute(
        select(CropProfile).options(selectinload(CropProfile.requirements)).order_by(CropProfile.name)
    )
    profiles = result.scalars().all()

    return [
        CropProfileResponse(
            id=p.id,
            name=p.name,
            description=p.description,
            source=p.source,
            requirements=[
                CropRequirementResponse(
                    id=r.id,
                    factor=r.factor,
                    min_value=r.min_value,
                    max_value=r.max_value,
                    unit=r.unit,
                    criticality=r.criticality,
                )
                for r in p.requirements
            ],
        )
        for p in profiles
    ]
