from datetime import datetime

from sqlalchemy.orm import Session

from app.models.application import Application, ApplicationData, Conversation, Message
from app.models.service import Service
from app.models.user import User


def get_or_create_user(db: Session, phone_number: str | None, preferred_language: str = "en") -> User:
    if phone_number:
        user = db.query(User).filter(User.phone_number == phone_number).one_or_none()
        if user:
            return user

    user = User(phone_number=phone_number, preferred_language=preferred_language)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_conversation(db: Session, user_id: int) -> Conversation:
    conversation = Conversation(user_id=user_id, status="open", started_at=datetime.utcnow())
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def add_message(db: Session, conversation_id: int, role: str, content: str) -> Message:
    message = Message(conversation_id=conversation_id, role=role, content=content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def start_application(db: Session, user_id: int, service_id: int, conversation_id: int | None = None) -> Application:
    service = db.get(Service, service_id)
    if service is None:
        raise ValueError("Service not found")

    reference_number = f"APP-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    application = Application(
        user_id=user_id,
        service_id=service_id,
        conversation_id=conversation_id,
        status="draft",
        reference_number=reference_number,
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


def upsert_application_data(db: Session, application_id: int, requirement_id: int, value: str | None) -> ApplicationData:
    record = (
        db.query(ApplicationData)
        .filter(ApplicationData.application_id == application_id, ApplicationData.requirement_id == requirement_id)
        .one_or_none()
    )
    if record:
        record.value = value
    else:
        record = ApplicationData(application_id=application_id, requirement_id=requirement_id, value=value)
        db.add(record)

    db.commit()
    db.refresh(record)
    return record
