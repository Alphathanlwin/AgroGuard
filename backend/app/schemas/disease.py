from pydantic import BaseModel


class DiseaseDetectionResponse(BaseModel):
    plantName: str
    scientificName: str
    healthStatus: str
    healthScore: int
    detectedDisease: str
    confidenceScore: int
    diseaseSeverity: str
    estimatedAffectedArea: str
    visibleSymptoms: list[str]
    possibleCauses: list[str]
    treatmentRecommendations: list[str]
    preventionRecommendations: list[str]
