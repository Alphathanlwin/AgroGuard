from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.crop_profile import CropProfile
from app.db.models.field import Field
from app.db.models.field_context_snapshot import FieldContextSnapshot
from app.db.session import get_db_session
from app.schemas.field import (
    FieldContextResponse,
    FieldResponse,
    SelectFieldRequest,
    SelectFieldResponse,
)

router = APIRouter(tags=["fields"])


@router.post(
    "/fields/select",
    response_model=SelectFieldResponse,
    status_code=status.HTTP_200_OK,
    summary="Select a seeded field and return its context + available crops",
)
async def select_field(
    request: SelectFieldRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
):
    field = await session.get(Field, request.field_id)
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")

    result = await session.execute(
        select(FieldContextSnapshot)
        .where(FieldContextSnapshot.field_id == field.id)
        .order_by(FieldContextSnapshot.captured_at.desc())
        .limit(1)
    )
    context = result.scalar_one_or_none()

    crops_result = await session.execute(select(CropProfile.name))
    crop_names = [row[0] for row in crops_result.all()]

    return SelectFieldResponse(
        field=FieldResponse(
            id=field.id,
            name=field.name,
            latitude=field.latitude,
            longitude=field.longitude,
            region_code=field.region_code,
            created_at=field.created_at,
        ),
        context=FieldContextResponse(
            soil_moisture=context.soil_moisture if context else None,
            ph=context.ph if context else None,
            temperature=context.temperature if context else None,
            humidity=context.humidity if context else None,
            light=context.light if context else None,
            rainfall=context.rainfall if context else None,
            captured_at=context.captured_at if context else None,
        ),
        available_crops=crop_names,
    )
