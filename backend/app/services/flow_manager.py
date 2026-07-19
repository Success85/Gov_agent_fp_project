from datetime import datetime

from sqlalchemy.orm import Session

from app.models.application import Application, ApplicationData, Conversation, Message
from app.models.service import Service
from app.models.requirement import Requirement
from app.models.steps import Step
from app.models.user import User
from app.services.grounding import GroundingContext, build_grounded_prompt
from app.services.intent import detect_intent, detect_confirmation, detect_skip
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

    conversation = Conversation(user_id=user_id, status="active", started_at=datetime.utcnow())
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
        .order_by(Requirement.id.asc())
        .all()
    )
    steps = db.query(Step).filter(Step.service_id == service_id).order_by(Step.step_no.asc()).all()

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


def get_next_missing_requirement(db: Session, application: Application) -> Requirement | None:
    """
    Finds the next requirement for this application's service that hasn't
    been fulfilled yet (either via a typed ApplicationData value, or via
    an uploaded document for requirements that need_upload).
    """
    requirements = (
        db.query(Requirement)
        .filter(Requirement.service_id == application.service_id)
        .order_by(Requirement.id.asc())
        .all()
    )
    answered_data_ids = {d.requirement_id for d in application.data if d.value}
    uploaded_ids = {u.requirement_id for u in application.uploads if u.requirement_id is not None}

    for requirement in requirements:
        if requirement.needs_upload:
            # Fulfilled by a real upload, OR by an explicit skip (N/A) on optional requirements
            if requirement.id not in uploaded_ids and requirement.id not in answered_data_ids:
                return requirement
        else:
            if requirement.id not in answered_data_ids:
                return requirement
    return None


def _requirement_prompt(requirement: Requirement, language: str) -> str:
    name = requirement.name_rw if language == "rw" else requirement.name
    if requirement.needs_upload:
        if language == "rw":
            return f"Nyamuneka ohereza (attach/upload) {name} ukoresheje buto yo kwohereza inyandiko."
        return f"Please upload your {name} using the attach button."
    if language == "rw":
        return f"Nyamuneka mbwira {name}."
    return f"Please provide your {name}."


def _application_summary_text(db: Session, application: Application, language: str) -> str:
    service = db.get(Service, application.service_id)
    requirements = (
        db.query(Requirement)
        .filter(Requirement.service_id == application.service_id)
        .order_by(Requirement.id.asc())
        .all()
    )

    header = "Incamake y'Ubusabe" if language == "rw" else "Application Summary"
    fee_label = "Amafaranga" if language == "rw" else "Fee"
    confirm_line = (
        "\n\nOhereza 'yego' kugira ngo mukomeze kwishyura, cyangwa 'oya' kugira ngo muhagarike."
        if language == "rw"
        else "\n\nReply 'yes' to proceed to payment, or 'no' to cancel."
    )

    lines = [f"**{header}: {service.name}**", ""]
    for requirement in requirements:
        label = requirement.name_rw if language == "rw" else requirement.name
        data = next((d for d in application.data if d.requirement_id == requirement.id), None)
        upload = next((u for u in application.uploads if u.requirement_id == requirement.id), None)
        if data and data.value:
            value = data.value
        elif upload:
            value = upload.file_name
        else:
            value = "—"
        lines.append(f"- {label}: {value}")

    lines.append("")
    lines.append(f"{fee_label}: {service.fee} RWF")
    lines.append(confirm_line)
    return "\n".join(lines)


def build_ai_reply(db: Session, conversation_id: int, message: str, service_id: int | None = None, language: str = "rw") -> tuple[Message, str, str | None, int | None]:
    conversation = db.get(Conversation, conversation_id)
    if conversation is None:
        raise ValueError("Conversation not found")

    # STATE: currently collecting a specific requirement's value
    if conversation.awaiting_requirement_id is not None:
        requirement = db.get(Requirement, conversation.awaiting_requirement_id)
        application = conversation.application

        if requirement is not None and application is not None:
            if not requirement.needs_upload:
                upsert_application_data(db, application.id, requirement.id, message.strip())
            elif not requirement.is_mandatory and detect_skip(message):
                upsert_application_data(db, application.id, requirement.id, "N/A")

            db.refresh(application)
            next_requirement = get_next_missing_requirement(db, application)

            if next_requirement is not None:
                conversation.awaiting_requirement_id = next_requirement.id
                db.add(conversation)
                db.commit()
                text = _requirement_prompt(next_requirement, language)
                assistant_message = add_message(db, conversation_id, "assistant", text)
                return assistant_message, "collecting_requirements", conversation.application.service.name, application.service_id

            conversation.awaiting_requirement_id = None
            conversation.awaiting_payment_confirmation = True
            db.add(conversation)
            db.commit()
            text = _application_summary_text(db, application, language)
            assistant_message = add_message(db, conversation_id, "assistant", text)
            return assistant_message, "awaiting_payment_confirmation", application.service.name, application.service_id

    # STATE: awaiting yes/no to proceed to payment
    if conversation.awaiting_payment_confirmation:
        confirmation = detect_confirmation(message)
        application = conversation.application

        if confirmation == "yes":
            conversation.awaiting_payment_confirmation = False
            db.add(conversation)
            db.commit()
            text = (
                "Nyamuneka koresha buto yo kwishyura kugira ngo urangize ubusabe bwawe."
                if language == "rw"
                else "Please use the payment button to complete your application."
            )
            assistant_message = add_message(db, conversation_id, "assistant", text)
            return assistant_message, "ready_for_payment", application.service.name if application else None, application.service_id if application else None

        if confirmation == "no":
            conversation.awaiting_payment_confirmation = False
            db.add(conversation)
            db.commit()
            text = "Nta kibazo. Ni iki kindi GovAgent yagufasha?" if language == "rw" else "No problem. What else can GovAgent help you with?"
            assistant_message = add_message(db, conversation_id, "assistant", text)
            return assistant_message, "general_query", None, None

        text = "Ohereza 'yego' cyangwa 'oya'." if language == "rw" else "Please reply 'yes' or 'no'."
        assistant_message = add_message(db, conversation_id, "assistant", text)
        return assistant_message, "awaiting_payment_confirmation", None, None

    # STATE: awaiting yes/no to START the application
    if conversation.pending_service_id is not None:
        confirmation = detect_confirmation(message)
        service = db.get(Service, conversation.pending_service_id)

        if confirmation == "yes":
            conversation.pending_service_id = None
            application = start_application(db, conversation.user_id, service.id, conversation_id)
            next_requirement = get_next_missing_requirement(db, application)

            if next_requirement is not None:
                conversation.awaiting_requirement_id = next_requirement.id
                db.add(conversation)
                db.commit()
                text = _requirement_prompt(next_requirement, language)
            else:
                conversation.awaiting_payment_confirmation = True
                db.add(conversation)
                db.commit()
                text = _application_summary_text(db, application, language)

            assistant_message = add_message(db, conversation_id, "assistant", text)
            return assistant_message, "collecting_requirements", service.name, service.id

        if confirmation == "no":
            conversation.pending_service_id = None
            db.add(conversation)
            db.commit()
            text = "Nta kibazo. Ni iki kindi GovAgent yagufasha?" if language == "rw" else "No problem. What else can GovAgent help you with?"
            assistant_message = add_message(db, conversation_id, "assistant", text)
            return assistant_message, "general_query", None, None

        text = (
            f"Mushaka gukomeza ubusabe bwa {service.name}? Ohereza 'yego' cyangwa 'oya'."
            if language == "rw"
            else f"Would you like to proceed with the {service.name} application? Reply 'yes' or 'no'."
        )
        assistant_message = add_message(db, conversation_id, "assistant", text)
        return assistant_message, "awaiting_confirmation", service.name, service.id

    # DEFAULT STATE: normal grounded chat, may open the confirmation gate
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
                steps=[item.instruction for item in overview["steps"]],
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
            steps=[item.instruction for item in overview["steps"]],
        )

    if selected_context is None:
        selected_context = GroundingContext(service_name="General Guidance")

    system_prompt = f"Intent: {intent_result.intent}"
    if intent_result.intent == "start_service" and selected_service_id is not None:
        conversation.pending_service_id = selected_service_id
        db.add(conversation)
        db.commit()
        system_prompt += (
            ". After answering, clearly ask: 'Would you like to proceed with the application now? "
            "Please reply yes or no.' (translate this question into the response language)"
        )

    prompt = build_grounded_prompt(message, selected_context, language=language)
    llm_client = LLMClient()
    assistant_response = llm_client.generate_reply(prompt, system_prompt=system_prompt).text
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
