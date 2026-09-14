import json

from fastapi import APIRouter, status
from fastapi.responses import StreamingResponse

from app.schemas.chat import ChatRequest
from app.services.llm import stream_chat

router = APIRouter(tags=["chat"])


@router.post("/chat", status_code=status.HTTP_200_OK, summary="Send a chat message")
async def chat(request: ChatRequest):
    messages = [{"role": m.role, "content": m.content} for m in request.messages]

    async def event_stream():
        async for chunk in stream_chat(messages, request.language):
            yield f"data: {json.dumps({'content': chunk, 'done': False})}\n\n"
        yield f"data: {json.dumps({'content': '', 'done': True})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
