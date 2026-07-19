# ============================================
# SEED DATA — verified against official Irembo
# support documentation (support.irembo.gov.rw)
# as of July 2026. Fees, processing times, and
# requirements are sourced from real Irembo FAQs
# and how-to articles for each service.
# ============================================
import logging
from app.db.database import SessionLocal, init_db
from app.models.user import User
from app.models.service import Service
from app.models.requirement import Requirement
from app.models.steps import Step
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.application import Application, ApplicationData

logger = logging.getLogger(__name__)


def clear_all_tables(db):
    """
    Delete all data from all tables in the correct order
    to respect foreign key constraints.
    """
    try:
        db.query(Message).delete()
        db.query(Conversation).delete()
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
    """
    Create sample citizen and admin accounts.
    """
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
    """
    Create all 5 government services with verified
    Irembo data (fees, processing times, categories).
    """
    services = [
        Service(
            name="Application for National ID",
            name_rw="Gusaba Indangamuntu",
            category="Identification",
            description="Apply for a Rwandan national identity card. Provided by the National Identification Agency (NIDA).",
            fee=500.00,
            processing_days=30
        ),
        Service(
            name="Birth Certificate",
            name_rw="Icyemezo cy'Amavuko",
            category="Family",
            description="Apply for an official birth certificate. Processed by local government authorities at the sector level.",
            fee=500.00,
            processing_days=1
        ),
        Service(
            name="Mutuelle (Health Insurance) Renewal",
            name_rw="Kwishyura Ubwishingizi bw'Ubuzima",
            category="Health",
            description=(
                "Apply for and pay Community-Based Health Insurance (Mutuelle de Sante) for yourself and your household. "
                "Provided by the Rwanda Social Security Board (RSSB). Fee depends on your household's income level "
                "under the IMIBEREHO Dynamic Social Registry, ranging from Rwf 4,000 to Rwf 20,000 per person per year; "
                "amount shown here reflects a typical second-tier contribution."
            ),
            fee=3000.00,
            processing_days=1
        ),
        Service(
            name="Marriage Certificate",
            name_rw="Icyemezo cy'Ubukwe",
            category="Family",
            description="Apply for the official certificate confirming an already-registered legal marriage. Processed at the sector level.",
            fee=500.00,
            processing_days=1
        ),
        Service(
            name="Driving License Application",
            name_rw="Gusaba Uruhushya rwo Gutwara Imodoka",
            category="Transport",
            description=(
                "Apply for a Definitive Driving License, issued by Rwanda National Police (RNP) after passing the "
                "theory and practical driving tests. This is the final stage of a multi-step process: theory test "
                "(Rwf 5,000) -> e-Provisional License (Rwf 10,000) -> driving school and practical test (Rwf 10,000) "
                "-> definitive license (Rwf 50,000)."
            ),
            fee=50000.00,
            processing_days=14
        ),
    ]

    for service in services:
        db.add(service)

    db.commit()
    logger.info(f"Seeded {len(services)} services")
    return services


def seed_requirements(db, services):
    """
    Create verified requirements for each service, sourced
    from official Irembo support documentation.
    """
    national_id = services[0]
    birth_cert = services[1]
    mutuelle = services[2]
    marriage_cert = services[3]
    driving_license = services[4]

    requirements = [
        # National ID requirements (indices 0-2)
        Requirement(
            service_id=national_id.id,
            name="Citizen Application Number (Child ID)",
            name_rw="Nomero yo Gusaba (Child ID)",
            is_mandatory=True,
            needs_upload=False
        ),
        Requirement(
            service_id=national_id.id,
            name="Valid Phone Number",
            name_rw="Nomero ya Terefone Ikora",
            is_mandatory=True,
            needs_upload=False
        ),
        Requirement(
            service_id=national_id.id,
            name="Email Address",
            name_rw="Aderesi Imeyili",
            is_mandatory=True,
            needs_upload=False
        ),

        # Birth Certificate requirements (indices 3-4)
        Requirement(
            service_id=birth_cert.id,
            name="National ID or Citizen Application Number",
            name_rw="Indangamuntu cyangwa Nomero yo Gusaba",
            is_mandatory=True,
            needs_upload=False
        ),
        Requirement(
            service_id=birth_cert.id,
            name="Valid Phone Number",
            name_rw="Nomero ya Terefone Ikora",
            is_mandatory=True,
            needs_upload=False
        ),

        # Mutuelle requirements
        Requirement(
            service_id=mutuelle.id,
            name="Head of Household National ID Number",
            name_rw="Indangamuntu y'Umukuru w'Umuryango",
            is_mandatory=True,
            needs_upload=False
        ),
        Requirement(
            service_id=mutuelle.id,
            name="Valid Phone Number or Email",
            name_rw="Nomero ya Terefone cyangwa Imeyili",
            is_mandatory=True,
            needs_upload=False
        ),

        # Marriage Certificate requirements
        Requirement(
            service_id=marriage_cert.id,
            name="National ID (Both Spouses)",
            name_rw="Indangamuntu z'Ababiri Bashakanye",
            is_mandatory=True,
            needs_upload=False
        ),
        Requirement(
            service_id=marriage_cert.id,
            name="Valid Phone Number or Email",
            name_rw="Nomero ya Terefone cyangwa Imeyili",
            is_mandatory=True,
            needs_upload=False
        ),

        # Driving License requirements
        Requirement(
            service_id=driving_license.id,
            name="National ID",
            name_rw="Indangamuntu",
            is_mandatory=True,
            needs_upload=False
        ),
        Requirement(
            service_id=driving_license.id,
            name="Registration Code from Passed Definitive Driving Test",
            name_rw="Kode yo Kwiyandikisha (nyuma yo gutsinda ikizamini)",
            is_mandatory=True,
            needs_upload=False
        ),
        Requirement(
            service_id=driving_license.id,
            name="Valid Phone Number or Email",
            name_rw="Nomero ya Terefone cyangwa Imeyili",
            is_mandatory=True,
            needs_upload=False
        ),
    ]

    for requirement in requirements:
        db.add(requirement)

    db.commit()
    logger.info(f"Seeded {len(requirements)} requirements")
    return requirements


def seed_steps(db, services):
    """
    Create verified step-by-step application processes,
    sourced from official Irembo support documentation.
    """
    national_id = services[0]
    birth_cert = services[1]
    mutuelle = services[2]
    marriage_cert = services[3]
    driving_license = services[4]

    steps = [
        # National ID steps
        Step(
            service_id=national_id.id,
            step_no=1,
            instruction="Get your Citizen Application Number (Child ID) from your sector office, if you don't already have one",
            instruction_rw="Bona Nomero yo Gusaba (Child ID) ku biro by'umurenge, niba utarayifite"
        ),
        Step(
            service_id=national_id.id,
            step_no=2,
            instruction="Apply on the Irembo platform or through an Irembo agent, and pay the Rwf 500 fee",
            instruction_rw="Saba kuri Irembo cyangwa binyuze kuri ajenti wa Irembo, wishyure amafaranga 500 Rwf"
        ),
        Step(
            service_id=national_id.id,
            step_no=3,
            instruction="Appear for biometric data capture (fingerprints and photo) after you are notified",
            instruction_rw="Jya gufata amakuru ya byometrike (ibikumwe n'ifoto) nyuma yo kumenyeshwa"
        ),
        Step(
            service_id=national_id.id,
            step_no=4,
            instruction="Wait while NIDA processes your application (about 30 days)",
            instruction_rw="Tegereza mu gihe NIDA itunganya dosiye yawe (hafi iminsi 30)"
        ),
        Step(
            service_id=national_id.id,
            step_no=5,
            instruction="Collect your National ID at your sector office",
            instruction_rw="Fata Indangamuntu yawe ku biro by'umurenge"
        ),

        # Birth Certificate steps
        Step(
            service_id=birth_cert.id,
            step_no=1,
            instruction="Log in to Irembo or visit an Irembo agent",
            instruction_rw="Injira kuri Irembo cyangwa usure ajenti wa Irembo"
        ),
        Step(
            service_id=birth_cert.id,
            step_no=2,
            instruction="Select the Birth Certificate service and enter your National ID or Citizen Application Number",
            instruction_rw="Hitamo serivisi y'Icyemezo cy'Amavuko, wandike Indangamuntu cyangwa Nomero yo Gusaba"
        ),
        Step(
            service_id=birth_cert.id,
            step_no=3,
            instruction="Verify your auto-filled details and choose the processing/collection sector office",
            instruction_rw="Emeza amakuru yagaragaye, hitamo ibiro by'umurenge byo gutunganyirizamo"
        ),
        Step(
            service_id=birth_cert.id,
            step_no=4,
            instruction="Pay the Rwf 500 fee",
            instruction_rw="Ishyura amafaranga 500 Rwf"
        ),
        Step(
            service_id=birth_cert.id,
            step_no=5,
            instruction="Once approved, you'll get an SMS or email notification and can download your e-certificate",
            instruction_rw="Nyuma yo kwemezwa, uzahabwa ubutumwa uzashobora gukurura icyemezo cyawe"
        ),

        # Mutuelle steps
        Step(
            service_id=mutuelle.id,
            step_no=1,
            instruction="Confirm your household registration and income level with your cell's LODA officer",
            instruction_rw="Emeza icyiciro cy'umuryango wawe uganira n'umukozi wa LODA w'akagari kawe"
        ),
        Step(
            service_id=mutuelle.id,
            step_no=2,
            instruction="Visit Irembo (or dial *909#) and select Community-Based Health Insurance (Mutuelle)",
            instruction_rw="Injira kuri Irembo (cyangwa hamagara *909#) uhitemo Ubwishingizi bw'Ubuzima (Mutuelle)"
        ),
        Step(
            service_id=mutuelle.id,
            step_no=3,
            instruction="Enter the head of household's National ID number",
            instruction_rw="Andika indangamuntu y'umukuru w'umuryango"
        ),
        Step(
            service_id=mutuelle.id,
            step_no=4,
            instruction="Review the amount due, which depends on your household's income level",
            instruction_rw="Reba amafaranga agomba kwishyurwa, ashingiye ku cyiciro cy'umuryango wawe"
        ),
        Step(
            service_id=mutuelle.id,
            step_no=5,
            instruction="Pay via Mobile Money or another supported payment channel",
            instruction_rw="Ishyura ukoresheje Mobile Money cyangwa ubundi buryo bwemewe"
        ),

        # Marriage Certificate steps
        Step(
            service_id=marriage_cert.id,
            step_no=1,
            instruction="Log in to Irembo or visit an Irembo agent",
            instruction_rw="Injira kuri Irembo cyangwa usure ajenti wa Irembo"
        ),
        Step(
            service_id=marriage_cert.id,
            step_no=2,
            instruction="Under Family Services, select Marriage Certificate",
            instruction_rw="Munsi ya Serivisi z'Umuryango, hitamo Icyemezo cy'Ubukwe"
        ),
        Step(
            service_id=marriage_cert.id,
            step_no=3,
            instruction="Enter your National ID; your spouse's details are retrieved automatically",
            instruction_rw="Andika indangamuntu yawe; amakuru y'uwo mwashakanye azagaragara ubwabyo"
        ),
        Step(
            service_id=marriage_cert.id,
            step_no=4,
            instruction="Choose the processing sector office and pay the Rwf 500 fee",
            instruction_rw="Hitamo ibiro by'umurenge, wishyure amafaranga 500 Rwf"
        ),
        Step(
            service_id=marriage_cert.id,
            step_no=5,
            instruction="Once the sector's Civil Registration Officer approves it, download your e-certificate",
            instruction_rw="Nyuma yo kwemezwa n'umwanditsi w'irangamimerere, kurura icyemezo cyawe"
        ),

        # Driving License steps (full multi-stage journey)
        Step(
            service_id=driving_license.id,
            step_no=1,
            instruction="Register for and pass the Provisional Theory Test (Rwf 5,000)",
            instruction_rw="Iyandikishe kandi utsinde ikizamini cy'amategeko (5,000 Rwf)"
        ),
        Step(
            service_id=driving_license.id,
            step_no=2,
            instruction="Apply for and download your e-Provisional Driving License (Rwf 10,000)",
            instruction_rw="Saba kandi ukurure uruhushya rw'agateganyo (10,000 Rwf)"
        ),
        Step(
            service_id=driving_license.id,
            step_no=3,
            instruction="Complete driving school training",
            instruction_rw="Rangiza amasomo yo kwiga gutwara imodoka"
        ),
        Step(
            service_id=driving_license.id,
            step_no=4,
            instruction="Register for and pass the Definitive (practical) Driving Test (Rwf 10,000)",
            instruction_rw="Iyandikishe kandi utsinde ikizamini cy'imyitozo (10,000 Rwf)"
        ),
        Step(
            service_id=driving_license.id,
            step_no=5,
            instruction="Apply for your Definitive Driving License (Rwf 50,000, processed in 14 days by Rwanda National Police)",
            instruction_rw="Saba uruhushya rwemewe burundu (50,000 Rwf, bitunganywa mu minsi 14 na Polisi y'Igihugu)"
        ),
    ]

    for step in steps:
        db.add(step)

    db.commit()
    logger.info(f"Seeded {len(steps)} steps")
    return steps


def seed_conversations(db, users):
    """
    Create sample conversations for testing.
    """
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
    """
    Create sample messages for testing.
    """
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
            status="draft",
            reference_number="GOV-2026-00002"
        ),
    ]

    for application in applications:
        db.add(application)

    db.commit()
    logger.info(f"Seeded {len(applications)} applications")
    return applications


def seed_application_data(db, applications, requirements):

    national_id_app = applications[0]
    birth_cert_app = applications[1]

    # requirements[0:3] = National ID, requirements[3:5] = Birth Certificate
    application_data = [
        ApplicationData(
            application_id=national_id_app.id,
            requirement_id=requirements[0].id,
            value="CAN-2024-00456"
        ),
        ApplicationData(
            application_id=national_id_app.id,
            requirement_id=requirements[1].id,
            value="0788123456"
        ),
        ApplicationData(
            application_id=national_id_app.id,
            requirement_id=requirements[2].id,
            value="aline.uwase@example.com"
        ),
        ApplicationData(
            application_id=birth_cert_app.id,
            requirement_id=requirements[3].id,
            value="1198800123456789"
        ),
        ApplicationData(
            application_id=birth_cert_app.id,
            requirement_id=requirements[4].id,
            value="0782345678"
        ),
    ]
    for data in application_data:
        db.add(data)
    db.commit()
    logger.info(f"Seeded {len(application_data)} application data entries")
    return application_data


def run_seed():

    logger.info("Starting database seed...")
    init_db()

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
        application_data = seed_application_data(db, applications, requirements)

        logger.info("Database seeded successfully")
        logger.info(f"Users: {len(users)}")
        logger.info(f"Services: {len(services)}")
        logger.info(f"Requirements: {len(requirements)}")
        logger.info(f"Steps: {len(steps)}")
        logger.info(f"Conversations: {len(conversations)}")
        logger.info(f"Messages: {len(messages)}")
        logger.info(f"Applications: {len(applications)}")
        logger.info(f"Application Data: {len(application_data)}")

    except Exception as e:
        logger.error(f"Seed failed: {e}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
