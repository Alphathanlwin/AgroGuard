from app.schemas.base import APIModel


class NDVIResponse(APIModel):
    labels: list[str]
    vim: list[float]
    viq: list[float]
