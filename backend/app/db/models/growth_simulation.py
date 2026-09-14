from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.growth_simulation_event import GrowthEvent


class GrowthSimulation(Base):
    __tablename__ = "growth_simulations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    field_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("fields.id", ondelete="CASCADE"), nullable=False, index=True
    )
    crop_profile_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("crop_profiles.id", ondelete="CASCADE"), nullable=False
    )
    scenario_type: Mapped[str] = mapped_column(String(30), nullable=False)
    seed: Mapped[str] = mapped_column(String(80), nullable=False)
    is_illustrative: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    events: Mapped[list[GrowthEvent]] = relationship(
        backref="simulation", cascade="all, delete-orphan", passive_deletes=True
    )
