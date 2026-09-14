from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CropRequirement(Base):
    __tablename__ = "crop_requirements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    crop_profile_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("crop_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    factor: Mapped[str] = mapped_column(String(50), nullable=False)
    min_value: Mapped[float] = mapped_column(Float, nullable=False)
    max_value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    criticality: Mapped[str] = mapped_column(String(20), nullable=False)
