"""Plan 8: LookCoach assistant chat."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..database import get_db
from ..services import assistant

router = APIRouter()


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=assistant.MAX_MESSAGE_CHARS)


@router.post("/chat")
def chat(body: ChatRequest, user_id: int = 1, db: Session = Depends(get_db)):
    try:
        return assistant.chat(db, user_id, body.message)
    except assistant.AssistantUnavailable as e:
        raise HTTPException(503, "Asystent jest niedostępny — brak działającego modelu AI (klucz OpenRouter lub Ollama).") from e


@router.get("/history")
def get_history(user_id: int = 1, db: Session = Depends(get_db)):
    return assistant.history(db, user_id)


@router.delete("/history")
def clear_history(user_id: int = 1, db: Session = Depends(get_db)):
    return {"deleted": assistant.clear(db, user_id)}
