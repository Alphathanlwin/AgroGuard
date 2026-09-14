from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.sensor_observation import SensorObservation


class SensorDevice(Base):
    __tablename__ = "sensor_devices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    field_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("fields.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    transport_type: Mapped[str] = mapped_column(String(50), nullable=False)
    device_id: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    is_simulated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_stale: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_seen_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(UTC),
    )
    observations: Mapped[list[SensorObservation]] = relationship(
        backref="device", cascade="all, delete-orphan", passive_deletes=True
    )
