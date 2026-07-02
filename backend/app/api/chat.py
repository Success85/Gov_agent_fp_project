from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.schemas import ConversationCreate, ConversationRead, MessageCreate, MessageRead
from app.services.flow_manager import add_message, create_conversation

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/start", response_model=ConversationRead, status_code=status.HTTP_201_CREATED)
def start_chat(payload: ConversationCreate, db: Session = Depends(get_db)):
    user = db.get(User, payload.user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return create_conversation(db, payload.user_id)


@router.post("/{conversation_id}/messages", response_model=MessageRead, status_code=status.HTTP_201_CREATED)
def post_message(conversation_id: int, payload: MessageCreate, db: Session = Depends(get_db)):
    return add_message(db, conversation_id, payload.role, payload.content)
