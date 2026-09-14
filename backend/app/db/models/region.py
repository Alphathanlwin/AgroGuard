from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Region(Base):
    __tablename__ = "regions"

    pcode: Mapped[str] = mapped_column(String(10), primary_key=True)
    name_en: Mapped[str] = mapped_column(String(100), nullable=False)
    name_my: Mapped[str] = mapped_column(String(100), nullable=False)
