import json

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


def _parse_sse_data(body: str) -> list[dict]:
    return [
        json.loads(line.removeprefix("data: "))
        for line in body.splitlines()
        if line.startswith("data: ")
    ]


@pytest.mark.asyncio
async def test_chat_returns_valid_sse_json_without_api_key() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/chat",
            json={"messages": [{"role": "user", "content": "How is my crop?"}]},
        )

    assert response.status_code == 200
    events = _parse_sse_data(response.text)
    assert events[-1] == {"content": "", "done": True}
    assert events[0]["done"] is False
    assert "How is my crop?" in events[0]["content"]


@pytest.mark.asyncio
async def test_crop_explanation_returns_valid_sse_json_without_api_key() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/crop-explanation",
            json={
                "soil_pH": 6.5,
                "rainfall_mm": 100,
                "temperature_c": 28,
                "crop": "Maize",
            },
        )

    assert response.status_code == 200
    events = _parse_sse_data(response.text)
    assert events[-1] == {"content": "", "done": True}
    assert events[0]["done"] is False
    assert "Maize" in events[0]["content"]
