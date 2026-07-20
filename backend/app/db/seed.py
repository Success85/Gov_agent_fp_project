from datetime import datetime, timezone
import logging
from app.db.database import SessionLocal, create_tables
from app.models.user import User
from app.models.service import Service
from app.models.requirement import Requirement
from app.models.steps import Step
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.application import Application, ApplicationData
from app.models.upload import Upload
from app.models.payment import Payment

logger = logging.getLogger(__name__)

def clear_all_tables(db):
   
    try:
        db.query(Message).delete()
        db.query(Conversation).delete()
        db.query(Upload).delete()
        db.query(Payment).delete()
        db.query(ApplicationData).delete()
        db.query(Application).delete()
        db.query(Requirement).delete()
        db.query(Step).delete()
        db.query(Service).delete()
        db.query(User).delete()
        db.commit()
        logger.info("All tables cleared successfully")
    except Exception as e:
        db.rollback()
        logger.error(f"Error clearing tables: {e}")
        raise


def seed_users(db):
   
    users = [
        User(
            phone_number="0781234567",
            preferred_language="rw"
        ),
        User(
            phone_number="0782345678",
            preferred_language="rw"
        ),
        User(
            phone_number="0783456789",
            preferred_language="en"
        ),
    ]

    for user in users:
        db.add(user)

    db.commit()
    logger.info(f"Seeded {len(users)} users")
    return users


def seed_services(db):
  
    services = [
        Service(
            name="Application for National ID",
            name_rw="Gusaba Indangamuntu",
            category="Identification",
            description="Apply for a Rwandan national identity card",
            fee=500.00,
            processing_days=30
        ),
        Service(
            name="Birth Certificate",
            name_rw="Icyemezo cy'Amavuko",
            category="Family",
            description="Apply for an official birth certificate",
            fee=500.00,
            processing_days=1
        ),
    ]

    for service in services:
        db.add(service)

    db.commit()
    logger.info(f"Seeded {len(services)} services")
    return services


def seed_requirements(db, services):
   
    national_id = services[0]
    birth_cert = services[1]

    requirements = [
        # National ID requirements
        Requirement(
            service_id=national_id.id,
            name="Birth Certificate",
            name_rw="Icyemezo cy'Amavuko",
            is_mandatory=True,
            needs_upload=True
        ),
        Requirement(
            service_id=national_id.id,
            name="Passport Photo",
            name_rw="Ifoto ya Pasiporo",
            is_mandatory=True,
            needs_upload=True
        ),
        Requirement(
            service_id=national_id.id,
            name="Proof of Residence",
            name_rw="Icyemezo cy'Aho Utuye",
            is_mandatory=True,
            needs_upload=True
        ),

        # Birth Certificate requirements
        Requirement(
            service_id=birth_cert.id,
            name="Parent National ID",
            name_rw="Indangamuntu y'Umubyeyi",
            is_mandatory=True,
            needs_upload=True
        ),
        Requirement(
            service_id=birth_cert.id,
            name="Hospital Birth Record",
            name_rw="Inyandiko y'Ivuka",
            is_mandatory=True,
            needs_upload=True
        ),
        Requirement(
            service_id=birth_cert.id,
            name="Marriage Certificate",
            name_rw="Icyemezo cy'Ubukwe",
            is_mandatory=False,
            needs_upload=True
        ),
    ]

    for requirement in requirements:
        db.add(requirement)

    db.commit()
    logger.info(f"Seeded {len(requirements)} requirements")
    return requirements


def seed_steps(db, services):
    
    national_id = services[0]
    birth_cert = services[1]

    steps = [
        # National ID steps
        Step(
            service_id=national_id.id,
            step_no=1,
            instruction="Log in to your Irembo account",
            instruction_rw="Injira kuri konti yawe ya Irembo"
        ),
        Step(
            service_id=national_id.id,
            step_no=2,
            instruction="Select National ID Application service",
            instruction_rw="Hitamo serivisi yo gusaba indangamuntu"
        ),
        Step(
            service_id=national_id.id,
            step_no=3,
            instruction="Fill in your personal details",
            instruction_rw="Uzuza amakuru yawe bwite"
        ),
        Step(
            service_id=national_id.id,
            step_no=4,
            instruction="Upload required documents",
            instruction_rw="Ohereza inyandiko zisabwa"
        ),
        Step(
            service_id=national_id.id,
            step_no=5,
            instruction="Pay the application fee using Mobile Money",
            instruction_rw="Ishyura ukoresheje Mobile Money"
        ),

        # Birth Certificate steps
        Step(
            service_id=birth_cert.id,
            step_no=1,
            instruction="Log in to your Irembo account",
            instruction_rw="Injira kuri konti yawe ya Irembo"
        ),
        Step(
            service_id=birth_cert.id,
            step_no=2,
            instruction="Select Birth Certificate service",
            instruction_rw="Hitamo serivisi y'icyemezo cy'amavuko"
        ),
        Step(
            service_id=birth_cert.id,
            step_no=3,
            instruction="Enter the child's details",
            instruction_rw="Injiza amakuru y'umwana"
        ),
        Step(
            service_id=birth_cert.id,
            step_no=4,
            instruction="Upload parent identification documents",
            instruction_rw="Ohereza inyandiko z'ababyeyi"
        ),
        Step(
            service_id=birth_cert.id,
            step_no=5,
            instruction="Pay the processing fee using Mobile Money",
            instruction_rw="Ishyura ukoresheje Mobile Money"
        ),
    ]

    for step in steps:
        db.add(step)

    db.commit()
    logger.info(f"Seeded {len(steps)} steps")
    return steps


def seed_conversations(db, users):
    
    conversations = [
        Conversation(
            user_id=users[0].id,
            status="completed"
        ),
        Conversation(
            user_id=users[1].id,
            status="active"
        ),
    ]

    for conversation in conversations:
        db.add(conversation)

    db.commit()
    logger.info(f"Seeded {len(conversations)} conversations")
    return conversations


def seed_messages(db, conversations):
    
    messages = [
        Message(
            conversation_id=conversations[0].id,
            role="user",
            content="Nshaka gusaba indangamuntu",
            input_type="text"
        ),
        Message(
            conversation_id=conversations[0].id,
            role="assistant",
            content="Nzakufasha gusaba indangamuntu. Ibikenewe ni ibi...",
            input_type="text"
        ),
        Message(
            conversation_id=conversations[1].id,
            role="user",
            content="Nshaka icyemezo cy'amavuko",
            input_type="voice"
        ),
        Message(
            conversation_id=conversations[1].id,
            role="assistant",
            content="Nzakufasha kubona icyemezo cy'amavuko...",
            input_type="text"
        ),
    ]

    for message in messages:
        db.add(message)

    db.commit()
    logger.info(f"Seeded {len(messages)} messages")
    return messages


def seed_applications(db, users, services):
    
    national_id = services[0]
    birth_cert = services[1]

    applications = [
        Application(
            user_id=users[0].id,
            service_id=national_id.id,
            status="submitted",
            reference_number="GOV-2026-00001"
        ),
        Application(
            user_id=users[1].id,
            service_id=birth_cert.id,
            status="in_progress",
            reference_number=None
        ),
    ]

    for application in applications:
        db.add(application)

    db.commit()
    logger.info(f"Seeded {len(applications)} applications")
    return applications


def seed_application_data(db, applications):
    
    national_id_app = applications[0]
    birth_cert_app = applications[1]

    application_data = [
        # Completed National ID application answers
        ApplicationData(
            application_id=national_id_app.id,
            field_name="full_name",
            field_value="Aline Uwase"
        ),
        ApplicationData(
            application_id=national_id_app.id,
            field_name="date_of_birth",
            field_value="1995-03-15"
        ),
        ApplicationData(
            application_id=national_id_app.id,
            field_name="district",
            field_value="Kigali"
        ),
        ApplicationData(
            application_id=national_id_app.id,
            field_name="sector",
            field_value="Nyarugenge"
        ),

        # Partial Birth Certificate answers
        ApplicationData(
            application_id=birth_cert_app.id,
            field_name="child_name",
            field_value="Kalisa Jean"
        ),
        ApplicationData(
            application_id=birth_cert_app.id,
            field_name="birth_date",
            field_value="2026-01-10"
        ),
    ]

    for data in application_data:
        db.add(data)

    db.commit()
    logger.info(
        f"Seeded {len(application_data)} application data entries"
    )
    return application_data


def seed_payments(db, applications):
   
    submitted_app = applications[0]
    inprogress_app = applications[1]

    payments = [
        Payment(
            application_id=submitted_app.id,
            transaction_reference="FLW-DEMO0001",
            amount=500.00,
            status="confirmed",
            proof_reference="PROOF-DEMO-001",
            paid_at=datetime.now(timezone.utc)
        ),
        Payment(
            application_id=inprogress_app.id,
            transaction_reference="FLW-DEMO0002",
            amount=500.00,
            status="pending"
        ),
    ]

    for payment in payments:
        db.add(payment)

    db.commit()
    logger.info(f"Seeded {len(payments)} payments")
    return payments


def seed_uploads(db, applications):
   
    submitted_app = applications[0]

    uploads = [
        Upload(
            application_id=submitted_app.id,
            file_name="birth_certificate.pdf",
            file_path=f"storage/uploads/{submitted_app.id}/birth_certificate.pdf",
            file_type="application/pdf",
            file_size_kb=512
        ),
        Upload(
            application_id=submitted_app.id,
            file_name="passport_photo.jpg",
            file_path=f"storage/uploads/{submitted_app.id}/passport_photo.jpg",
            file_type="image/jpeg",
            file_size_kb=256
        ),
    ]

    for upload in uploads:
        db.add(upload)

    db.commit()
    logger.info(f"Seeded {len(uploads)} uploads")
    return uploads

def run_seed():
   
    logger.info("Starting database seed...")
    create_tables()

    db = SessionLocal()

    try:
        clear_all_tables(db)

        users = seed_users(db)
        services = seed_services(db)
        requirements = seed_requirements(db, services)
        steps = seed_steps(db, services)
        conversations = seed_conversations(db, users)
        messages = seed_messages(db, conversations)
        applications = seed_applications(db, users, services)
        application_data = seed_application_data(db, applications)
        payments = seed_payments(db, applications)
        uploads = seed_uploads(db, applications)

        logger.info("Database seeded successfully")
        logger.info(f"Users: {len(users)}")
        logger.info(f"Services: {len(services)}")
        logger.info(f"Requirements: {len(requirements)}")
        logger.info(f"Steps: {len(steps)}")
        logger.info(f"Conversations: {len(conversations)}")
        logger.info(f"Messages: {len(messages)}")
        logger.info(f"Applications: {len(applications)}")
        logger.info(f"Application Data: {len(application_data)}")
        logger.info(f"Payments: {len(payments)}")
        logger.info(f"Uploads: {len(uploads)}")

    except Exception as e:
        logger.error(f"Seed failed: {e}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    run_seed()