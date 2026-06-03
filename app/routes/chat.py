from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio

router = APIRouter()


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]


@router.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    async def generate():
        # Your streaming logic here
        # This is just an example - replace with your actual LLM streaming
        response_text = "This is streaming from FastAPI backend"

        for word in response_text.split():
            yield f"{word} "
            await asyncio.sleep(0.05)

    return StreamingResponse(
        generate(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
