from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class HealthUpdate(Base):
    __tablename__ = "health_updates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    township: Mapped[str] = mapped_column(String(100), nullable=False)
    crop_type: Mapped[str] = mapped_column(String(100), nullable=False)
    health_status: Mapped[str] = mapped_column(String(50), nullable=False)
    disease_details: Mapped[str | None] = mapped_column(Text, nullable=True)
    reported_by: Mapped[str] = mapped_column(String(100), nullable=False)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    reported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(UTC),
    )
