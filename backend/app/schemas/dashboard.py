from pydantic import BaseModel


class OverviewStats(BaseModel):
    townships: int
    records: int
    yield_: str
    rainfall: str


class CropDistribution(BaseModel):
    crop: str
    percent: float


class YieldByCrop(BaseModel):
    crop: str
    yield_: float


class DashboardResponse(BaseModel):
    overview: OverviewStats
    cropDistribution: list[CropDistribution]
    yieldByCrop: list[YieldByCrop]
