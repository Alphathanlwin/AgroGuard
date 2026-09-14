from app.schemas.base import APIModel


class RegionResponse(APIModel):
    pcode: str
    name_en: str
    name_my: str
