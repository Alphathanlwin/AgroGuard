from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class GrowthEvent(Base):
    __tablename__ = "growth_simulation_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    simulation_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("growth_simulations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    event_date: Mapped[str] = mapped_column(String(10), nullable=False)
    growth_stage: Mapped[str] = mapped_column(String(40), nullable=False)
    health_index: Mapped[int] = mapped_column(Integer, nullable=False)
    intervention: Mapped[str | None] = mapped_column(Text, nullable=True)
    risk_marker: Mapped[str | None] = mapped_column(String(100), nullable=True)
