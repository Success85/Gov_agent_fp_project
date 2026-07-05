from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.application import Conversation
from app.models.user import User
from app.schemas import ChatReply, ChatRequest, ConversationCreate, ConversationRead, MessageCreate, MessageRead
from app.services.flow_manager import add_message, build_ai_reply, create_conversation, get_or_create_user_by_phone

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatReply, status_code=status.HTTP_201_CREATED)
def chat_with_ai(payload: ChatRequest, db: Session = Depends(get_db)):
    user = None
    if payload.user_id is not None:
        user = db.get(User, payload.user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    else:
        if payload.phone_number is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="phone_number or user_id is required")
        user = get_or_create_user_by_phone(db, payload.phone_number, preferred_language=payload.preferred_language)

    conversation = None
    if payload.conversation_id is not None:
        conversation = db.get(Conversation, payload.conversation_id)
        if conversation is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    if conversation is None:
        conversation = create_conversation(db, user.id)

    add_message(db, conversation.id, "user", payload.message)
    assistant_message, intent, service_name, service_id = build_ai_reply(db, conversation.id, payload.message, payload.service_id)
    return ChatReply(
        conversation_id=conversation.id,
        user_id=user.id,
        intent=intent,
        service_name=service_name,
        assistant_message=assistant_message.content,
        assistant_message_id=assistant_message.id,
        service_id=service_id,
    )


@router.post("/start", response_model=ConversationRead, status_code=status.HTTP_201_CREATED)
def start_chat(payload: ConversationCreate, db: Session = Depends(get_db)):
    user = db.get(User, payload.user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return create_conversation(db, payload.user_id)


@router.post("/{conversation_id}/messages", response_model=MessageRead, status_code=status.HTTP_201_CREATED)
def post_message(conversation_id: int, payload: MessageCreate, db: Session = Depends(get_db)):
    return add_message(db, conversation_id, payload.role, payload.content)
