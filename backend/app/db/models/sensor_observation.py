from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SensorObservation(Base):
    __tablename__ = "sensor_observations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sensor_devices.id", ondelete="CASCADE"), nullable=False, index=True
    )
    event_id: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    humidity: Mapped[float | None] = mapped_column(Float, nullable=True)
    soil_moisture: Mapped[float | None] = mapped_column(Float, nullable=True)
    ph: Mapped[float | None] = mapped_column(Float, nullable=True)
    light: Mapped[float | None] = mapped_column(Float, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(UTC),
    )
