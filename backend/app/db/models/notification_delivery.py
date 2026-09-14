from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Notification(Base):
    __tablename__ = "notification_deliveries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    alert_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("alerts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    channel: Mapped[str] = mapped_column(String(30), default="telegram", nullable=False)
    destination_ref: Mapped[str] = mapped_column(String(120), default="demo", nullable=False)
    delivery_key: Mapped[str] = mapped_column(String(220), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    attempt_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_error_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
