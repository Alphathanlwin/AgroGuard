from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class NDVIMeasurement(Base):
    __tablename__ = "ndvi_measurements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    region_pcode: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(20), nullable=False)
    vim: Mapped[float] = mapped_column(Float, nullable=False)
    viq: Mapped[float] = mapped_column(Float, nullable=False)
