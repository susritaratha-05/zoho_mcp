from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, field_validator

from api.agent import stream_chat
from utils.config import settings
from utils.logger import get_logger

logger = get_logger("app")

app = FastAPI(
    title="PD HR Chatbot API",
    description="AI-powered HR assistant — Prodevans Technologies Pvt. Ltd.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request Model ──────────────────────────────────────────────────────────────
class ChatMessage(BaseModel):
    role:    str
    content: str


class ChatRequest(BaseModel):
    employee_email: str
    employee_name:  str = "Employee"
    employee_id:    str = ""
    access_token:   str                       # Zoho OAuth token from session
    conversation:   list[ChatMessage] = []

    @field_validator("employee_email")
    @classmethod
    def must_be_prodevans(cls, email_value: str) -> str:
        return str(email_value)   # domain already validated in frontend


# ── Endpoints ──────────────────────────────────────────────────────────────────
@app.get("/health")
async def health_check():
    return {"status": "ok", "model": settings.groq_model}


@app.post("/chat/stream")
async def chat_stream(chat_request: ChatRequest):
    """Stream HR assistant reply via SSE. Each event: data: <token>\\n\\n"""

    employee_info = {
        "name":  chat_request.employee_name,
        "id":    chat_request.employee_id,
        "email": chat_request.employee_email,
    }

    conversation_history = [message.model_dump() for message in chat_request.conversation]

    async def event_generator():
        try:
            async for response_chunk in stream_chat(
                conversation_messages = conversation_history,
                employee_info         = employee_info,
                access_token          = chat_request.access_token,
            ):
                safe_chunk = response_chunk.replace("\n", "\\n").replace("\r", "").replace("'", "\\'")
                yield f"data: {safe_chunk}\n\n"

        except Exception as streaming_error:
            logger.error(f"[App] Streaming error: {streaming_error}")
            yield f"data: Sorry, something went wrong. Please try again.\n\n"

        finally:
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control":    "no-cache",
            "X-Accel-Buffering": "no",
        },
    )