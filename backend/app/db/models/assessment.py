from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Assessment(Base):
    __tablename__ = "assessments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    field_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("fields.id", ondelete="CASCADE"), nullable=False, index=True
    )
    observation_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("sensor_observations.id", ondelete="SET NULL"), nullable=True
    )
    crop_profile_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("crop_profiles.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    health_score: Mapped[float] = mapped_column(Float, nullable=False)
    primary_risk: Mapped[str | None] = mapped_column(String(100), nullable=True)
    recommendation: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    confidence: Mapped[str] = mapped_column(String(20), default="high", nullable=False)
    decision_mode: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=lambda: datetime.now(UTC),
        default=lambda: datetime.now(UTC),
    )
