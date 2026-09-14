from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class FieldContextSnapshot(Base):
    __tablename__ = "field_context_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    field_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("fields.id", ondelete="CASCADE"), nullable=False, index=True
    )
    soil_moisture: Mapped[float | None] = mapped_column(Float, nullable=True)
    ph: Mapped[float | None] = mapped_column(Float, nullable=True)
    temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    humidity: Mapped[float | None] = mapped_column(Float, nullable=True)
    light: Mapped[float | None] = mapped_column(Float, nullable=True)
    rainfall: Mapped[float | None] = mapped_column(Float, nullable=True)
    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(UTC),
    )
