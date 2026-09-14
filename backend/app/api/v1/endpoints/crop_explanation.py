import json

from fastapi import APIRouter, status
from fastapi.responses import StreamingResponse

from app.schemas.crop_explanation import CropExplanationRequest
from app.services.llm import stream_crop_explanation

router = APIRouter(tags=["crop-explanation"])


@router.post("/crop-explanation", status_code=status.HTTP_200_OK, summary="Get AI crop explanation")
async def crop_explanation(request: CropExplanationRequest):
    async def event_stream():
        async for chunk in stream_crop_explanation(
            request.soil_pH,
            request.rainfall_mm,
            request.temperature_c,
            request.crop,
            request.language,
        ):
            yield f"data: {json.dumps({'content': chunk, 'done': False})}\n\n"
        yield f"data: {json.dumps({'content': '', 'done': True})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
