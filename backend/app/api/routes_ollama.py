from typing import List, Literal

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.config import OLLAMA_HOST

router = APIRouter(prefix="/api")


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"] = Field(default="user")
    content: str


class ChatRequest(BaseModel):
    model: str
    messages: List[ChatMessage]


@router.get("/models")
async def list_models() -> dict:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(f"{OLLAMA_HOST}/api/tags")
            response.raise_for_status()
            payload = response.json()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=503, detail=f"Unable to contact Ollama: {exc}") from exc

    models = payload.get("models") or []
    return {"models": [item["name"] for item in models if item.get("name")]}


@router.post("/chat")
async def chat(request: ChatRequest) -> dict:
    payload = {
        "model": request.model,
        "messages": [{"role": item.role, "content": item.content} for item in request.messages],
        "stream": False,
    }

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(f"{OLLAMA_HOST}/api/chat", json=payload)
            response.raise_for_status()
            result = response.json()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=503, detail=f"Ollama request failed: {exc}") from exc

    message = result.get("message") or {}
    response_text = message.get("content") or ""
    return {"response": response_text}
