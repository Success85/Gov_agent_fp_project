from datetime import datetime

from sqlalchemy.orm import Session

from pathlib import Path

from app.core.config import get_settings
from app.models.application import Application, ApplicationData, Conversation, GeneratedDocument, Message
from app.models.service import Service
from app.models.requirement import Requirement
from app.models.steps import Step
from app.models.user import User
from app.services.grounding import GroundingContext, build_grounded_prompt
from app.services.intent import detect_intent, detect_confirmation, detect_skip
from app.services.validation import validate_field
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

    name_label = "Amazina" if language == "rw" else "Full Name"
    lines = [f"**{header}: {service.name}**", f"{name_label}: {application.applicant_name or 'N/A'}", ""]
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


def _find_collected_email(application: Application) -> str | None:
    if application.payment_email:
        return application.payment_email
    for data in application.data:
        requirement = data.requirement
        if requirement and data.value and "email" in requirement.name.lower():
            return data.value
    return None


def build_ai_reply(db: Session, conversation_id: int, message: str, service_id: int | None = None, language: str = "rw") -> tuple[Message, str, str | None, int | None]:
    conversation = db.get(Conversation, conversation_id)
    if conversation is None:
        raise ValueError("Conversation not found")

    # STATE: collecting the applicant's full name (first step after confirming)
    if conversation.awaiting_applicant_name:
        application = conversation.application
        candidate = message.strip()
        if application is not None and len(candidate) >= 2 and any(c.isalpha() for c in candidate):
            application.applicant_name = candidate
            conversation.awaiting_applicant_name = False
            db.add(application)
            db.add(conversation)
            db.commit()
            db.refresh(application)

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
            return assistant_message, "collecting_requirements", application.service.name if application.service else None, application.service_id

        text = (
            "Nyamuneka tanga amazina yawe yuzuye (urugero: Aline Uwase)."
            if language == "rw"
            else "Please provide your full name (e.g. Aline Uwase)."
        )
        assistant_message = add_message(db, conversation_id, "assistant", text)
        return assistant_message, "awaiting_applicant_name", None, None

    # STATE: collecting the payment email (final step before payment)
    if conversation.awaiting_payment_email:
        application = conversation.application
        candidate = message.strip()
        if application is not None and "@" in candidate and "." in candidate.split("@")[-1]:
            application.payment_email = candidate
            conversation.awaiting_payment_email = False
            db.add(application)
            db.add(conversation)
            db.commit()
            text = (
                "Nyamuneka koresha buto yo kwishyura kugira ngo urangize ubusabe bwawe."
                if language == "rw"
                else "Please use the payment button to complete your application."
            )
            assistant_message = add_message(db, conversation_id, "assistant", text)
            return assistant_message, "ready_for_payment", application.service.name if application else None, application.service_id if application else None

        text = (
            "Ntibyagenze neza. Nyamuneka tanga imeyili yawe nyayo (urugero: aline@example.com)."
            if language == "rw"
            else "That doesn't look like a valid email. Please provide a valid email address (e.g. aline@example.com)."
        )
        assistant_message = add_message(db, conversation_id, "assistant", text)
        return assistant_message, "awaiting_payment_email", None, None

    # STATE: currently collecting a specific requirement's value
    if conversation.awaiting_requirement_id is not None:
        requirement = db.get(Requirement, conversation.awaiting_requirement_id)
        application = conversation.application

        if requirement is not None and application is not None:
            if not requirement.needs_upload:
                is_valid, validation_error = validate_field(requirement.validation_type, message.strip(), language)
                if not is_valid:
                    assistant_message = add_message(db, conversation_id, "assistant", validation_error)
                    return assistant_message, "collecting_requirements", application.service.name, application.service_id
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

            existing_email = _find_collected_email(application) if application else None
            if not existing_email:
                conversation.awaiting_payment_email = True
                db.add(conversation)
                db.commit()
                text = (
                    "Mbere yo gukomeza kwishyura, nyamuneka tanga imeyili yawe kugira ngo tubone kukoherereza inyemezabuguzi."
                    if language == "rw"
                    else "Before proceeding to payment, please provide your email address so we can send your payment receipt."
                )
                assistant_message = add_message(db, conversation_id, "assistant", text)
                return assistant_message, "awaiting_payment_email", application.service.name if application else None, application.service_id if application else None

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
            conversation.awaiting_applicant_name = True
            db.add(conversation)
            db.commit()
            text = (
                "Mbere yo gukomeza, nyamuneka tanga amazina yawe yuzuye."
                if language == "rw"
                else "Before we continue, please provide your full name."
            )
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


def generate_approval_document(db: Session, application: Application) -> GeneratedDocument:
    """
    Generates a real, printable PDF approval document for a successfully
    paid application, including all collected requirement answers, and
    saves a record of it.
    """
    from fpdf import FPDF

    settings = get_settings()
    storage_root = Path(settings.storage_dir)
    storage_root.mkdir(parents=True, exist_ok=True)

    service = application.service
    requirements = (
        db.query(Requirement)
        .filter(Requirement.service_id == application.service_id)
        .order_by(Requirement.id.asc())
        .all()
    )

    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(0, 87, 183)
    pdf.cell(0, 12, "GovAgent", ln=True, align="C")

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 8, "Official Application Approval Confirmation", ln=True, align="C")
    pdf.ln(6)

    pdf.set_draw_color(200, 200, 200)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(8)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, service.name if service else "Government Service", ln=True)
    pdf.ln(2)

    pdf.set_font("Helvetica", "", 11)

    def field(label, value):
        pdf.set_font("Helvetica", "B", 11)
        pdf.write(8, f"{label}: ")
        pdf.set_font("Helvetica", "", 11)
        pdf.write(8, str(value) if value else "N/A")
        pdf.ln(9)

    field("Applicant Name", application.applicant_name)
    field("Reference Number", application.reference_number)
    field("Status", "APPROVED")
    field("Fee Paid", f"{float(service.fee) if service else 0:.2f} RWF")
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Application Details", ln=True)
    pdf.set_draw_color(220, 220, 220)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(3)

    for requirement in requirements:
        data = next((d for d in application.data if d.requirement_id == requirement.id), None)
        upload = next((u for u in application.uploads if u.requirement_id == requirement.id), None)
        if data and data.value:
            value = data.value
        elif upload:
            value = upload.file_name
        else:
            value = "N/A"
        field(requirement.name, value)

    pdf.ln(6)
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(
        0, 6,
        "This document confirms that your application has been received, processed, "
        "and approved. Present this reference number at your chosen collection office, "
        "or check your registered email for further details."
    )

    filename = f"approval_{application.reference_number}.pdf"
    file_path = storage_root / filename
    pdf.output(str(file_path))

    document = GeneratedDocument(application_id=application.id, file_path=str(file_path))
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def _find_collection_location(application: Application) -> str | None:
    """
    Looks through the application's collected answers for anything that
    looks like a collection district/sector/office, to reference in the
    closing message.
    """
    keywords = ("collection", "processing office")
    exclude_keywords = ("biometric",)
    parts = []
    for data in application.data:
        requirement = data.requirement
        if requirement and data.value:
            name_lower = requirement.name.lower()
            if any(kw in name_lower for kw in keywords) and not any(ex in name_lower for ex in exclude_keywords):
                parts.append(data.value)
    if parts:
        return ", ".join(parts)
    return None


def build_closing_message(db: Session, application: Application, gateway_reference: str, language: str = "rw") -> str:
    """
    Builds a warm, grounded closing message via Gemini confirming payment,
    referencing the approval document, and inviting feedback.
    """
    service = application.service
    collection_location = _find_collection_location(application)

    system_prompts = {
        "rw": (
            "Uri GovAgent, umufasha w'ubwenge bw'ubukorikori ufasha abaturage muri serivisi za Leta kuri Irembo. "
            "Ubusabe bw'umukoresha bwemejwe kandi bwishyuwe neza. Andika ubutumwa bwo gusoza, bushyuha kandi "
            "bufite umwuka mwiza, bugaragaza: (1) ibyishimo byo kwemeza ko byagenze neza, (2) nomero y'ubwishyu "
            "n'iy'ubusabe, (3) uko azabona inyandiko ye (kureba imeyili cyangwa kujya ku biro by'aho yatoranyije), "
            "(4) amashimwe akomeye yo gukoresha GovAgent, (5) usabe ko yatanga igitekerezo/amanota ku serivisi. "
            "Ntukoreshe amagambo y'ikinyabwoko cyangwa make cyane; baza mu buryo bwuzuye kandi bushyuha."
        ),
        "en": (
            "You are GovAgent, an AI assistant helping citizens with Rwandan government services on Irembo. Address the applicant by their name if provided. "
            "The user's application has just been successfully approved and paid for. Write a warm, complete "
            "closing message that: (1) celebrates the successful confirmation, (2) states the payment reference "
            "and application reference numbers, (3) tells them how to get their document (check their email, or "
            "visit their chosen collection office), (4) thanks them warmly for using GovAgent, (5) invites them "
            "to rate their experience and leave feedback. Be warm and complete, not terse."
        ),
    }
    system_prompt = system_prompts.get(language, system_prompts["en"])

    details = (
        f"Applicant full name: {application.applicant_name or 'Applicant'}\n"
        f"Service: {service.name if service else 'N/A'}\n"
        f"Application reference number: {application.reference_number}\n"
        f"Payment reference number: {gateway_reference}\n"
        f"Fee paid: {float(service.fee) if service else 0:.2f} RWF\n"
        f"Collection location provided by applicant: {collection_location or 'Not specified - advise them to check their email or visit their nearest sector office'}\n"
    )

    llm_client = LLMClient()
    response = llm_client.generate_reply(details, system_prompt=system_prompt)

    if response.model in ("unavailable", "error"):
        collection_text = collection_location or (
            "your registered email or nearest sector office" if language != "rw"
            else "imeyili yawe cyangwa ibiro by'umurenge biri hafi yawe"
        )
        if language == "rw":
            return (
                f"Murakoze! Ubusabe bwanyu bwa {service.name if service else ''} bwemejwe kandi bwishyuwe neza.\n\n"
                f"Nomero y'ubusabe: {application.reference_number}\n"
                f"Nomero y'ubwishyu: {gateway_reference}\n\n"
                f"Nyamuneka mureba {collection_text} kugira ngo mubone inyandiko zanyu.\n\n"
                f"Murakoze gukoresha GovAgent!"
            )
        return (
            f"Thank you! Your {service.name if service else 'application'} has been successfully approved and paid for.\n\n"
            f"Application reference: {application.reference_number}\n"
            f"Payment reference: {gateway_reference}\n\n"
            f"Please check {collection_text} to collect your document.\n\n"
            f"Thank you for using GovAgent!"
        )

    return response.text
