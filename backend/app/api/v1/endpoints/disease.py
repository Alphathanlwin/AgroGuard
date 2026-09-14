from fastapi import APIRouter, UploadFile, status, HTTPException, Header
import traceback
from fastapi.concurrency import run_in_threadpool
from typing import Annotated

from app.schemas.disease import DiseaseDetectionResponse
from app.services.llm import get_disease_advice

try:
    from app.ml.disease_detection import predict_image
except ImportError:
    predict_image = None
    print("Warning: ML model files not found or missing dependencies.")

router = APIRouter(tags=["disease-detection"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE = 8 * 1024 * 1024


@router.post(
    "/disease-detect",
    response_model=DiseaseDetectionResponse,
    status_code=status.HTTP_200_OK,
    summary="Detect plant disease from an image",
)
async def disease_detect(
    file: UploadFile,
    accept_language: Annotated[str | None, Header()] = "en",
):
    language = "my" if accept_language and "my" in accept_language.lower() else "en"
    
    if file.content_type not in ALLOWED_TYPES:
        return DiseaseDetectionResponse(
            plantName="",
            scientificName="",
            healthStatus="Invalid file type. Please upload JPG, PNG, or WEBP.",
            healthScore=0,
            detectedDisease="",
            confidenceScore=0,
            diseaseSeverity="",
            estimatedAffectedArea="",
            visibleSymptoms=[],
            possibleCauses=[],
            treatmentRecommendations=["Upload a valid image file."],
            preventionRecommendations=[],
        )

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        return DiseaseDetectionResponse(
            plantName="",
            scientificName="",
            healthStatus="File too large. Maximum size is 8 MB.",
            healthScore=0,
            detectedDisease="",
            confidenceScore=0,
            diseaseSeverity="",
            estimatedAffectedArea="",
            visibleSymptoms=[],
            possibleCauses=[],
            treatmentRecommendations=["Choose a smaller image."],
            preventionRecommendations=[],
        )

    result = await _analyze_image(contents, file.content_type, language)
    return DiseaseDetectionResponse(**result)


async def _analyze_image(image_bytes: bytes, content_type: str, language: str) -> dict:
    if predict_image is None:
        raise HTTPException(status_code=503, detail="Machine learning models are not available. Please install PyTorch and train the model.")
        
    try:
        # Run the CPU-bound inference in a threadpool so we don't block the async event loop
        prediction = await run_in_threadpool(predict_image, image_bytes)
        
        is_healthy = prediction.get("is_healthy", False)
        plant_name = prediction.get("plant", "Unknown Plant")
        disease_name = prediction.get("disease", "Unknown Disease")
        confidence = prediction.get("confidence", 0)
        
        # Get dynamic advice from the LLM
        advice = await get_disease_advice(
            plant=plant_name,
            disease=disease_name,
            is_healthy=is_healthy,
            language=language
        )
        
        return {
            "plantName": plant_name,
            "scientificName": f"{plant_name} sp.",
            "healthStatus": "Healthy" if is_healthy else "Disease Detected",
            "healthScore": int(confidence) if is_healthy else max(0, 100 - int(confidence)),
            "detectedDisease": "None" if is_healthy else disease_name,
            "confidenceScore": int(confidence),
            "diseaseSeverity": "None" if is_healthy else "Moderate",
            "estimatedAffectedArea": "0%" if is_healthy else "Varies",
            "visibleSymptoms": advice.get("visibleSymptoms", []),
            "possibleCauses": advice.get("possibleCauses", []),
            "treatmentRecommendations": advice.get("treatmentRecommendations", []),
            "preventionRecommendations": advice.get("preventionRecommendations", []),
        }
    except Exception as e:
        print(f"ML Error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error analyzing image: {str(e)}")
