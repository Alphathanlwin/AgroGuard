from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.alert import Alert
from app.db.models.notification_delivery import Notification
from app.db.session import get_db_session
from app.schemas.alert import AlertResponse, NotificationResponse
from app.services.alerting import acknowledge_alert as acknowledge_alert_service
from app.services.alerting import resolve_alert as resolve_alert_service

router = APIRouter(tags=["alerts"])


@router.get(
    "/alerts",
    response_model=list[AlertResponse],
    status_code=status.HTTP_200_OK,
    summary="List alerts with optional field/status filter",
)
async def list_alerts(
    field_id: int | None = None,
    alert_status: str | None = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=200),
    session: Annotated[AsyncSession, Depends(get_db_session)] = None,
):
    query = select(Alert).order_by(Alert.opened_at.desc()).limit(limit)
    if field_id is not None:
        query = query.where(Alert.field_id == field_id)
    if alert_status:
        query = query.where(Alert.status == alert_status)
    result = await session.execute(query)
    return result.scalars().all()


@router.get(
    "/fields/{field_id}/alerts",
    response_model=list[AlertResponse],
    status_code=status.HTTP_200_OK,
    summary="List alerts for a specific field",
)
async def field_alerts(
    field_id: int,
    limit: int = Query(50, ge=1, le=200),
    session: Annotated[AsyncSession, Depends(get_db_session)] = None,
):
    result = await session.execute(
        select(Alert)
        .where(Alert.field_id == field_id)
        .order_by(Alert.opened_at.desc())
        .limit(limit)
    )
    return result.scalars().all()


@router.patch(
    "/alerts/{alert_id}/acknowledge",
    response_model=AlertResponse,
    status_code=status.HTTP_200_OK,
    summary="Acknowledge an alert",
)
async def acknowledge_alert(
    alert_id: int,
    session: Annotated[AsyncSession, Depends(get_db_session)] = None,
):
    alert = await acknowledge_alert_service(session, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.patch(
    "/alerts/{alert_id}/resolve",
    response_model=AlertResponse,
    status_code=status.HTTP_200_OK,
    summary="Resolve an alert",
)
async def resolve_alert(
    alert_id: int,
    session: Annotated[AsyncSession, Depends(get_db_session)] = None,
):
    alert = await resolve_alert_service(session, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.get(
    "/notifications",
    response_model=list[NotificationResponse],
    status_code=status.HTTP_200_OK,
    summary="List notification deliveries",
)
async def list_notifications(
    limit: int = Query(50, ge=1, le=200),
    session: Annotated[AsyncSession, Depends(get_db_session)] = None,
):
    result = await session.execute(
        select(Notification).order_by(Notification.id.desc()).limit(limit)
    )
    return result.scalars().all()
