from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.alert import Alert
from app.db.models.assessment import Assessment
from app.db.models.field import Field
from app.db.models.notification_delivery import Notification
from app.services.telegram import format_alert_message, send_telegram_message


async def create_alert_for_assessment(
    session: AsyncSession,
    *,
    field: Field,
    assessment: Assessment,
) -> tuple[Alert | None, Notification | None]:
    if assessment.status not in {"warning", "critical"}:
        return None, None

    now = datetime.now(UTC)
    cooldown_start = now - timedelta(hours=1)
    result = await session.execute(
        select(Alert)
        .where(
            Alert.field_id == field.id,
            Alert.risk_type == assessment.primary_risk,
            Alert.opened_at >= cooldown_start,
        )
        .order_by(Alert.opened_at.desc())
    )
    recent = result.scalar_one_or_none()

    fingerprint = f"{field.id}:{assessment.primary_risk}:{assessment.status}"
    if recent:
        suppressed = Notification(
            alert_id=recent.id,
            channel="telegram",
            destination_ref="cooldown",
            delivery_key=f"{recent.fingerprint}:cooldown:{now.isoformat()}",
            status="suppressed",
            attempt_count=0,
            last_error_code="cooldown_active",
        )
        session.add(suppressed)
        return recent, suppressed

    alert = Alert(
        field_id=field.id,
        assessment_id=assessment.id,
        fingerprint=fingerprint,
        severity=assessment.status,
        risk_type=assessment.primary_risk or "unknown",
        message=assessment.recommendation or "No recommendation",
        status="open",
        opened_at=now,
    )
    session.add(alert)
    await session.flush()

    from app.core.config import get_settings
    settings = get_settings()

    delivery = Notification(
        alert_id=alert.id,
        channel="telegram",
        destination_ref=settings.telegram_chat_id or "not-configured",
        delivery_key=f"{fingerprint}:{assessment.id}",
        status="pending",
        attempt_count=1,
    )
    result_tg = send_telegram_message(
        format_alert_message(
            field_name=field.name,
            risk_type=assessment.primary_risk or "unknown",
            recommendation=assessment.recommendation or "No recommendation",
        )
    )
    delivery.status = result_tg.status
    delivery.last_error_code = result_tg.error_code
    if result_tg.status == "sent":
        delivery.sent_at = now
    session.add(delivery)
    return alert, delivery


async def acknowledge_alert(session: AsyncSession, alert_id: int) -> Alert | None:
    alert = await session.get(Alert, alert_id)
    if not alert:
        return None
    alert.status = "acknowledged"
    alert.acknowledged_at = datetime.now(UTC)
    await session.commit()
    await session.refresh(alert)
    return alert


async def resolve_alert(session: AsyncSession, alert_id: int) -> Alert | None:
    alert = await session.get(Alert, alert_id)
    if not alert:
        return None
    alert.status = "resolved"
    alert.resolved_at = datetime.now(UTC)
    await session.commit()
    await session.refresh(alert)
    return alert
