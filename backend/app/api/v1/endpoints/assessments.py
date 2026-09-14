from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.assessment import Assessment
from app.db.models.sensor_device import SensorDevice
from app.db.session import get_db_session
from app.schemas.assessment import AssessmentResponse, FieldStatusResponse

router = APIRouter(tags=["assessments"])


@router.get(
    "/fields/{field_id}/current-status",
    response_model=FieldStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get the latest assessment for a field",
)
async def get_field_current_status(
    field_id: int,
    session: Annotated[AsyncSession, Depends(get_db_session)],
):
    result = await session.execute(
        select(Assessment)
        .where(Assessment.field_id == field_id)
        .order_by(Assessment.created_at.desc())
        .limit(1)
    )
    latest = result.scalar_one_or_none()

    devices_result = await session.execute(
        select(
            func.count(SensorDevice.id),
            func.count(SensorDevice.id).filter(SensorDevice.is_stale == False),  # noqa: E712
            func.count(SensorDevice.id).filter(SensorDevice.is_stale == True),  # noqa: E712
        ).where(SensorDevice.field_id == field_id)
    )
    total, active, stale = devices_result.one()

    return FieldStatusResponse(
        field_id=field_id,
        latest_assessment=AssessmentResponse(
            id=latest.id,
            field_id=latest.field_id,
            observation_id=latest.observation_id,
            crop_profile_id=latest.crop_profile_id,
            status=latest.status,
            health_score=latest.health_score,
            primary_risk=latest.primary_risk,
            recommendation=latest.recommendation,
            evidence=latest.evidence,
            decision_mode=latest.decision_mode,
            created_at=latest.created_at,
        ) if latest else None,
        device_count=total,
        active_devices=active,
        stale_devices=stale,
    )


@router.get(
    "/fields/{field_id}/assessment-history",
    response_model=list[AssessmentResponse],
    status_code=status.HTTP_200_OK,
    summary="Get assessment timeline for a field",
)
async def get_field_assessment_history(
    field_id: int,
    session: Annotated[AsyncSession, Depends(get_db_session)],
):
    result = await session.execute(
        select(Assessment)
        .where(Assessment.field_id == field_id)
        .order_by(Assessment.created_at.desc())
    )
    assessments = result.scalars().all()

    return [
        AssessmentResponse(
            id=a.id,
            field_id=a.field_id,
            observation_id=a.observation_id,
            crop_profile_id=a.crop_profile_id,
            status=a.status,
            health_score=a.health_score,
            primary_risk=a.primary_risk,
            recommendation=a.recommendation,
            evidence=a.evidence,
            decision_mode=a.decision_mode,
            created_at=a.created_at,
        )
        for a in assessments
    ]
