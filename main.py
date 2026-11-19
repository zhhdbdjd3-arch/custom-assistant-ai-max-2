import os
from typing import Any
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

KILO_BASE_URL = os.getenv("AI_BASE_URL", "https://ai-gateway.kilo.ai/api/v1").rstrip("/")
AI_MODEL = os.getenv("AI_MODEL", "nvidia/nemotron-3.5-super-vl:free")
AI_API_KEY = os.getenv("AI_API_KEY", "")

app = FastAPI(title="Custom Assistant AI MAX API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str | None = None
    messages: list[dict[str, Any]] | None = None
    conversation_id: str | None = None
    image: str | None = None
    image_base64: str | None = None
    temperature: float = 0.7
    system_prompt: str | None = None

@app.get("/")
def root():
    return {"status": "ok", "service": "Custom Assistant AI MAX"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/chat")
async def chat(req: ChatRequest):
    messages = req.messages or []
    if not messages and req.message:
        messages = [{"role": "user", "content": req.message}]

    if not messages:
        raise HTTPException(status_code=400, detail="Напиши сообщение.")

    # Optional system prompt from the app; otherwise use a friendly default.
    if req.system_prompt:
        messages = [{"role": "system", "content": req.system_prompt}] + messages
    elif not any(m.get("role") == "system" for m in messages):
        messages = [{"role": "system", "content": "Ты дружелюбный, внимательный ИИ-помощник. Отвечай ясно и по делу на языке пользователя."}] + messages

    # Attach an image to the latest user message if the app sends base64.
    image_data = req.image_base64 or req.image
    if image_data:
        if image_data.startswith("data:"):
            image_url = image_data
        else:
            image_url = "data:image/jpeg;base64," + image_data
        for item in reversed(messages):
            if item.get("role") == "user":
                content = item.get("content", "")
                if isinstance(content, str):
                    item["content"] = [
                        {"type": "text", "text": content},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ]
                break

    headers = {"Content-Type": "application/json"}
    if AI_API_KEY:
        headers["Authorization"] = f"Bearer {AI_API_KEY}"

    payload = {
        "model": AI_MODEL,
        "messages": messages,
        "temperature": max(0, min(2, req.temperature)),
        "stream": False,
    }

    try:
        async with httpx.AsyncClient(timeout=90) as client:
            response = await client.post(
                f"{KILO_BASE_URL}/chat/completions",
                headers=headers,
                json=payload,
            )
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=f"Не удалось связаться с ИИ-сервисом: {exc}")

    if response.status_code >= 400:
        detail = response.text[:1200]
        raise HTTPException(status_code=response.status_code, detail=f"Ответ Kilo: {detail}")

    data = response.json()
    try:
        answer = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        raise HTTPException(status_code=502, detail="ИИ-сервис вернул неожиданный ответ.")

    if isinstance(answer, list):
        answer = "".join(part.get("text", "") for part in answer if isinstance(part, dict))

    return {
        "reply": answer,
        "message": answer,
        "conversation_id": req.conversation_id,
        "model": AI_MODEL,
    }
