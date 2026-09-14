from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.crop_profile import CropProfile
from app.db.models.crop_requirement import CropRequirement
from app.db.models.field_context_snapshot import FieldContextSnapshot
from app.db.session import get_db_session
from app.schemas.crop_profile import CropSuitabilityRequest, CropSuitabilityResponse
from app.services.suitability import score_suitability

router = APIRouter(tags=["crop-suitability"])


@router.post(
    "/crop-suitability",
    response_model=CropSuitabilityResponse,
    status_code=status.HTTP_200_OK,
    summary="Score a field against a crop profile",
)
async def evaluate_crop_suitability(
    request: CropSuitabilityRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
):
    crop_profile = await session.get(CropProfile, request.crop_profile_id)
    if not crop_profile:
        raise HTTPException(status_code=404, detail="Crop profile not found")

    req_result = await session.execute(
        select(CropRequirement).where(
            CropRequirement.crop_profile_id == crop_profile.id
        )
    )
    requirements = list(req_result.scalars().all())

    snap_result = await session.execute(
        select(FieldContextSnapshot)
        .where(FieldContextSnapshot.field_id == request.field_id)
        .order_by(FieldContextSnapshot.captured_at.desc())
        .limit(1)
    )
    context = snap_result.scalar_one_or_none()

    return score_suitability(crop_profile, requirements, context)
