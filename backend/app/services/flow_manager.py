from datetime import datetime

from sqlalchemy.orm import Session

from app.models.application import Application, ApplicationData, Conversation, Message
from app.models.service import Requirement, Service, Step
from app.models.user import User
from app.services.grounding import GroundingContext, build_grounded_prompt
from app.services.intent import detect_intent
from app.services.llm_client import LLMClient


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
    user = db.get(User, user_id)
    if user is None:
        raise ValueError("User not found")

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


def get_service_overview(db: Session, service_id: int) -> dict:
    service = db.get(Service, service_id)
    if service is None:
        raise ValueError("Service not found")

    requirements = (
        db.query(Requirement)
        .filter(Requirement.service_id == service_id)
        .order_by(Requirement.order_index.asc())
        .all()
    )
    steps = db.query(Step).filter(Step.service_id == service_id).order_by(Step.order_index.asc()).all()

    return {
        "service": service,
        "requirements": requirements,
        "steps": steps,
    }


def list_services(db: Session) -> list[Service]:
    return db.query(Service).order_by(Service.name.asc()).all()


def get_or_create_conversation(db: Session, user_id: int, conversation_id: int | None = None) -> Conversation:
    if conversation_id is not None:
        conversation = db.get(Conversation, conversation_id)
        if conversation is None:
            raise ValueError("Conversation not found")
        return conversation
    return create_conversation(db, user_id)


def build_ai_reply(db: Session, conversation_id: int, message: str, service_id: int | None = None) -> tuple[Message, str, str | None, int | None]:
    conversation = db.get(Conversation, conversation_id)
    if conversation is None:
        raise ValueError("Conversation not found")

    available_services = [item.name for item in db.query(Service).all()]
    intent_result = detect_intent(message, available_services=available_services)

    selected_service_id = service_id
    selected_service_name: str | None = None
    selected_context = None

    if intent_result.service_name:
        matched_service = db.query(Service).filter(Service.name == intent_result.service_name).one_or_none()
        if matched_service is not None:
            selected_service_id = matched_service.id
            selected_service_name = matched_service.name
            overview = get_service_overview(db, matched_service.id)
            selected_context = GroundingContext(
                service_name=matched_service.name,
                description=matched_service.description,
                fee=matched_service.fee,
                requirements=[item.name for item in overview["requirements"]],
                steps=[item.description for item in overview["steps"]],
            )

    if selected_context is None and selected_service_id is not None:
        overview = get_service_overview(db, selected_service_id)
        selected_service = overview["service"]
        selected_service_name = selected_service.name
        selected_context = GroundingContext(
            service_name=selected_service.name,
            description=selected_service.description,
            fee=selected_service.fee,
            requirements=[item.name for item in overview["requirements"]],
            steps=[item.description for item in overview["steps"]],
        )

    if selected_context is None:
        selected_context = GroundingContext(service_name="General Guidance")

    prompt = build_grounded_prompt(message, selected_context)
    llm_client = LLMClient()
    assistant_response = llm_client.generate_reply(prompt, system_prompt=f"Intent: {intent_result.intent}").text
    assistant_message = add_message(db, conversation_id, "assistant", assistant_response)
    return assistant_message, intent_result.intent, selected_service_name, selected_service_id


def get_application_summary(application: Application) -> dict:
    return {
        "service_name": application.service.name if application.service else None,
        "total_payments": len(application.payments),
        "total_uploaded_files": len(application.uploads),
    }


def start_application(db: Session, user_id: int, service_id: int, conversation_id: int | None = None) -> Application:
    user = db.get(User, user_id)
    if user is None:
        raise ValueError("User not found")

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


def get_or_create_user_by_phone(db: Session, phone_number: str | None, preferred_language: str = "en") -> User:
    return get_or_create_user(db, phone_number=phone_number, preferred_language=preferred_language)
