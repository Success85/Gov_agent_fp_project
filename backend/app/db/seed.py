# ============================================
# SEED DATA — verified against official Irembo
# support documentation AND the real Irembo
# application-flow guide provided by the team.
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
    users = [
        User(phone_number="0781234567", preferred_language="rw"),
        User(phone_number="0782345678", preferred_language="rw"),
        User(phone_number="0783456789", preferred_language="en"),
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
            description="Apply for a Rwandan national identity card. Provided by the National Identification Agency (NIDA).",
            fee=500.00,
            processing_days=30
        ),
        Service(
            name="Birth Record",
            name_rw="Kwandikisha Amavuko",
            category="Family",
            description=(
                "Register a new birth in the civil registry (creates the official birth record). "
                "This is required before a Birth Certificate can be issued. Involves details about "
                "the child (or self), both parents, a witness, and the declarant."
            ),
            fee=1500.00,
            processing_days=1
        ),
        Service(
            name="Birth Certificate",
            name_rw="Icyemezo cy'Amavuko",
            category="Family",
            description="Request an official birth certificate for an already-registered birth record. Processed at the sector level.",
            fee=500.00,
            processing_days=1
        ),
        Service(
            name="Marriage Declaration",
            name_rw="Kwiyandikisha ku Bukwe",
            category="Family",
            description=(
                "Declare an upcoming civil marriage at least 21 days in advance. Requires details for both "
                "spouses and 3 supporting documents. Free if scheduled on a Thursday; Rwf 50,000 on other days."
            ),
            fee=50000.00,
            processing_days=1
        ),
        Service(
            name="Mutuelle (Health Insurance) Renewal",
            name_rw="Kwishyura Ubwishingizi bw'Ubuzima",
            category="Health",
            description=(
                "Apply for and pay Community-Based Health Insurance (Mutuelle de Sante) for an individual "
                "or a household/organization in bulk. Requires downloading a household template, filling "
                "it in offline, and uploading it back. Provided by the Rwanda Social Security Board (RSSB). "
                "Fee depends on income level under the IMIBEREHO Dynamic Social Registry (Rwf 4,000-20,000/person/year); "
                "amount shown here reflects a typical second-tier contribution."
            ),
            fee=3000.00,
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
    national_id, birth_record, birth_cert, marriage_decl, mutuelle, driving_license = services

    requirements = [
        # ---- National ID (indices 0-5) ----
        Requirement(service_id=national_id.id, name="Applying For (Self or Bulk)", name_rw="Urasaba Wowe cyangwa Benshi", is_mandatory=True, needs_upload=False),
        Requirement(service_id=national_id.id, name="Child ID", name_rw="Child ID", is_mandatory=True, needs_upload=False),
        Requirement(service_id=national_id.id, name="Biometric Sector", name_rw="Umurenge wo Gufata Ibimenyetso", is_mandatory=True, needs_upload=False),
        Requirement(service_id=national_id.id, name="Biometric Date", name_rw="Itariki yo Gufata Ibimenyetso", is_mandatory=True, needs_upload=False),
        Requirement(service_id=national_id.id, name="Collection District", name_rw="Akarere ko Kuraho", is_mandatory=True, needs_upload=False),
        Requirement(service_id=national_id.id, name="Collection Sector", name_rw="Umurenge wo Kuraho", is_mandatory=True, needs_upload=False),

        # ---- Birth Record (indices 6-19) ----
        Requirement(service_id=birth_record.id, name="Applying For (Self or Child)", name_rw="Urasaba Wowe cyangwa Umwana", is_mandatory=True, needs_upload=False),
        Requirement(service_id=birth_record.id, name="Applicant ID Type and Number", name_rw="Ubwoko n'Inomero y'Indangamuntu y'Usaba", is_mandatory=True, needs_upload=False),
        Requirement(service_id=birth_record.id, name="Mother's ID Type and Number", name_rw="Ubwoko n'Inomero y'Indangamuntu ya Nyina", is_mandatory=True, needs_upload=False),
        Requirement(service_id=birth_record.id, name="Father's ID Type and Number", name_rw="Ubwoko n'Inomero y'Indangamuntu ya Se", is_mandatory=True, needs_upload=False),
        Requirement(service_id=birth_record.id, name="Do Parents Live in Rwanda? (Yes/No)", name_rw="Ese Ababyeyi Batuye mu Rwanda?", is_mandatory=True, needs_upload=False),
        Requirement(service_id=birth_record.id, name="Parents' Residential Address", name_rw="Aho Ababyeyi Batuye", is_mandatory=True, needs_upload=False),
        Requirement(service_id=birth_record.id, name="Witness ID Type and Number", name_rw="Ubwoko n'Inomero y'Indangamuntu y'Umuhamya", is_mandatory=True, needs_upload=False),
        Requirement(service_id=birth_record.id, name="Witness Phone Number", name_rw="Nomero ya Terefone y'Umuhamya", is_mandatory=True, needs_upload=False),
        Requirement(service_id=birth_record.id, name="Declarant ID Type and Number", name_rw="Ubwoko n'Inomero y'Indangamuntu y'Utangaza", is_mandatory=True, needs_upload=False),
        Requirement(service_id=birth_record.id, name="Declarant Phone Number", name_rw="Nomero ya Terefone y'Utangaza", is_mandatory=True, needs_upload=False),
        Requirement(service_id=birth_record.id, name="Processing Office (District and Sector)", name_rw="Ibiro Bitunganya (Akarere n'Umurenge)", is_mandatory=True, needs_upload=False),
        Requirement(service_id=birth_record.id, name="Mother's Passport (if applicable)", name_rw="Pasiporo ya Nyina (niba ihari)", is_mandatory=False, needs_upload=True),
        Requirement(service_id=birth_record.id, name="Father's Passport (if applicable)", name_rw="Pasiporo ya Se (niba ihari)", is_mandatory=False, needs_upload=True),
        Requirement(service_id=birth_record.id, name="Declarant's Passport Copy (if applicable)", name_rw="Kopi ya Pasiporo y'Utangaza (niba ihari)", is_mandatory=False, needs_upload=True),

        # ---- Birth Certificate (indices 20-22) ----
        Requirement(service_id=birth_cert.id, name="Applying For (Self or Child)", name_rw="Urasaba Wowe cyangwa Umwana", is_mandatory=True, needs_upload=False),
        Requirement(service_id=birth_cert.id, name="Processing Office District", name_rw="Akarere k'Ibiro Bitunganya", is_mandatory=True, needs_upload=False),
        Requirement(service_id=birth_cert.id, name="Processing Office Sector", name_rw="Umurenge w'Ibiro Bitunganya", is_mandatory=True, needs_upload=False),

        # ---- Marriage Declaration (indices 23-38) ----
        Requirement(service_id=marriage_decl.id, name="Country of Marriage (Rwanda or Abroad)", name_rw="Igihugu Uzashyingirwamo", is_mandatory=True, needs_upload=False),
        Requirement(service_id=marriage_decl.id, name="Marriage Date (at least 21 days from today)", name_rw="Itariki y'Ubukwe (nibura iminsi 21 uhereye none)", is_mandatory=True, needs_upload=False),
        Requirement(service_id=marriage_decl.id, name="Wife's ID Type and Number", name_rw="Ubwoko n'Inomero y'Indangamuntu y'Umugore", is_mandatory=True, needs_upload=False),
        Requirement(service_id=marriage_decl.id, name="Wife's Residence (District/Sector or Country/City)", name_rw="Aho Umugore Atuye", is_mandatory=True, needs_upload=False),
        Requirement(service_id=marriage_decl.id, name="Wife's Profession", name_rw="Umwuga w'Umugore", is_mandatory=True, needs_upload=False),
        Requirement(service_id=marriage_decl.id, name="Wife's Occupation", name_rw="Akazi k'Umugore", is_mandatory=True, needs_upload=False),
        Requirement(service_id=marriage_decl.id, name="Wife's Phone Number", name_rw="Nomero ya Terefone y'Umugore", is_mandatory=True, needs_upload=False),
        Requirement(service_id=marriage_decl.id, name="Wife's Email Address", name_rw="Imeyili y'Umugore", is_mandatory=True, needs_upload=False),
        Requirement(service_id=marriage_decl.id, name="Husband's ID Type and Number", name_rw="Ubwoko n'Inomero y'Indangamuntu y'Umugabo", is_mandatory=True, needs_upload=False),
        Requirement(service_id=marriage_decl.id, name="Husband's Residence (District/Sector or Country/City)", name_rw="Aho Umugabo Atuye", is_mandatory=True, needs_upload=False),
        Requirement(service_id=marriage_decl.id, name="Husband's Profession", name_rw="Umwuga w'Umugabo", is_mandatory=True, needs_upload=False),
        Requirement(service_id=marriage_decl.id, name="Husband's Occupation", name_rw="Akazi k'Umugabo", is_mandatory=True, needs_upload=False),
        Requirement(service_id=marriage_decl.id, name="Husband's Phone Number", name_rw="Nomero ya Terefone y'Umugabo", is_mandatory=True, needs_upload=False),
        Requirement(service_id=marriage_decl.id, name="Husband's Email Address", name_rw="Imeyili y'Umugabo", is_mandatory=True, needs_upload=False),
        Requirement(service_id=marriage_decl.id, name="Wife's Birth Certificate", name_rw="Icyemezo cy'Amavuko cy'Umugore", is_mandatory=True, needs_upload=True),
        Requirement(service_id=marriage_decl.id, name="Husband's Birth Certificate", name_rw="Icyemezo cy'Amavuko cy'Umugabo", is_mandatory=True, needs_upload=True),
        Requirement(service_id=marriage_decl.id, name="Wife's Certificate of Being Single", name_rw="Icyemezo ko Umugore Atarashaka", is_mandatory=True, needs_upload=True),

        # ---- Mutuelle (indices 39-43) ----
        Requirement(service_id=mutuelle.id, name="Application Scope (Bulk or Single)", name_rw="Ubwoko bw'Ubusabe (Benshi cyangwa Umwe)", is_mandatory=True, needs_upload=False),
        Requirement(service_id=mutuelle.id, name="Application Type (Individual/Company/Corporate/NGO/FBO/Other)", name_rw="Ubwoko bw'Usaba", is_mandatory=True, needs_upload=False),
        Requirement(service_id=mutuelle.id, name="Organization Name and TIN (if applicable)", name_rw="Izina ry'Ikigo na TIN (niba bihari)", is_mandatory=False, needs_upload=False),
        Requirement(service_id=mutuelle.id, name="Coverage Year", name_rw="Umwaka w'Ubwishingizi", is_mandatory=True, needs_upload=False),
        Requirement(service_id=mutuelle.id, name="Filled Household Template", name_rw="Urupapuro rw'Umuryango Rwuzuye", is_mandatory=True, needs_upload=True),

        # ---- Driving License (indices 44-46) ----
        Requirement(service_id=driving_license.id, name="National ID", name_rw="Indangamuntu", is_mandatory=True, needs_upload=False),
        Requirement(service_id=driving_license.id, name="Registration Code from Passed Definitive Driving Test", name_rw="Kode yo Kwiyandikisha (nyuma yo gutsinda ikizamini)", is_mandatory=True, needs_upload=False),
        Requirement(service_id=driving_license.id, name="Valid Phone Number or Email", name_rw="Nomero ya Terefone cyangwa Imeyili", is_mandatory=True, needs_upload=False),
    ]

    for requirement in requirements:
        db.add(requirement)
    db.commit()
    logger.info(f"Seeded {len(requirements)} requirements")
    return requirements


def seed_steps(db, services):
    national_id, birth_record, birth_cert, marriage_decl, mutuelle, driving_license = services

    steps = [
        Step(service_id=national_id.id, step_no=1, instruction="Select 'Application for National ID'", instruction_rw="Hitamo 'Gusaba Indangamuntu'"),
        Step(service_id=national_id.id, step_no=2, instruction="Review the processing time, fee, and provider (NIDA)", instruction_rw="Reba igihe bitwara, ikiguzi, n'ikigo gitanga (NIDA)"),
        Step(service_id=national_id.id, step_no=3, instruction="Select who you're applying for: self or bulk", instruction_rw="Hitamo urasaba wowe cyangwa benshi"),
        Step(service_id=national_id.id, step_no=4, instruction="Fill in application details: Child ID, biometric sector/date, collection office", instruction_rw="Uzuza amakuru: Child ID, umurenge wo gufata ibimenyetso/itariki, ibiro byo kuraho"),
        Step(service_id=national_id.id, step_no=5, instruction="Review the summary and proceed to payment", instruction_rw="Reba incamake hanyuma ukomeze kwishyura"),

        Step(service_id=birth_record.id, step_no=1, instruction="Choose 'Birth Record' (as opposed to Birth Certificate) and note the Rwf 1,500 fee", instruction_rw="Hitamo 'Kwandikisha Amavuko' (byatandukanye n'Icyemezo cy'Amavuko), wemeze amafaranga 1,500"),
        Step(service_id=birth_record.id, step_no=2, instruction="Select who you're applying for: self or child", instruction_rw="Hitamo urasaba wowe cyangwa umwana"),
        Step(service_id=birth_record.id, step_no=3, instruction="Provide the applicant's ID type and number", instruction_rw="Tanga ubwoko n'inomero y'indangamuntu y'usaba"),
        Step(service_id=birth_record.id, step_no=4, instruction="Provide both parents' details, including whether they live in Rwanda and their address", instruction_rw="Tanga amakuru y'ababyeyi bombi, harimo niba batuye mu Rwanda n'aho batuye"),
        Step(service_id=birth_record.id, step_no=5, instruction="Provide witness details (ID and phone number)", instruction_rw="Tanga amakuru y'umuhamya (indangamuntu na terefone)"),
        Step(service_id=birth_record.id, step_no=6, instruction="Provide declarant details (ID and phone number)", instruction_rw="Tanga amakuru y'utangaza (indangamuntu na terefone)"),
        Step(service_id=birth_record.id, step_no=7, instruction="Select the processing office (district and sector, or embassy if abroad)", instruction_rw="Hitamo ibiro bitunganya (akarere n'umurenge, cyangwa ambasade niba uri hanze)"),
        Step(service_id=birth_record.id, step_no=8, instruction="Upload supporting passports if applicable, review the summary, and proceed to payment", instruction_rw="Ohereza pasiporo niba zisabwa, urebe incamake, hanyuma ukomeze kwishyura"),

        Step(service_id=birth_cert.id, step_no=1, instruction="Choose 'Birth Certificate' for an already-registered birth record", instruction_rw="Hitamo 'Icyemezo cy'Amavuko' ku mavuko yamaze kwandikwa"),
        Step(service_id=birth_cert.id, step_no=2, instruction="Select self or child, then choose the processing district and sector", instruction_rw="Hitamo wowe cyangwa umwana, hanyuma uhitemo akarere n'umurenge"),
        Step(service_id=birth_cert.id, step_no=3, instruction="Review the summary and proceed to payment", instruction_rw="Reba incamake hanyuma ukomeze kwishyura"),

        Step(service_id=marriage_decl.id, step_no=1, instruction="Select the country of marriage and a date at least 21 days from today", instruction_rw="Hitamo igihugu uzashyingirwamo n'itariki nibura iminsi 21 uhereye none"),
        Step(service_id=marriage_decl.id, step_no=2, instruction="Provide the wife's ID, residence, profession, occupation, phone, and email", instruction_rw="Tanga amakuru y'umugore: indangamuntu, aho atuye, umwuga, akazi, terefone, imeyili"),
        Step(service_id=marriage_decl.id, step_no=3, instruction="Provide the husband's ID, residence, profession, occupation, phone, and email", instruction_rw="Tanga amakuru y'umugabo: indangamuntu, aho atuye, umwuga, akazi, terefone, imeyili"),
        Step(service_id=marriage_decl.id, step_no=4, instruction="Upload both birth certificates and the wife's certificate of being single", instruction_rw="Ohereza ibyemezo by'amavuko byombi n'icyemezo ko umugore atarashaka"),
        Step(service_id=marriage_decl.id, step_no=5, instruction="Review the summary and proceed to payment (free on Thursdays, Rwf 50,000 other days)", instruction_rw="Reba incamake hanyuma ukomeze kwishyura (ku wa kane ni ubuntu, indi minsi ni 50,000 Rwf)"),

        Step(service_id=mutuelle.id, step_no=1, instruction="Choose bulk or single application", instruction_rw="Hitamo ubusabe bw'benshi cyangwa bw'umwe"),
        Step(service_id=mutuelle.id, step_no=2, instruction="Select the application type: individual, company, corporate, NGO, FBO, or other", instruction_rw="Hitamo ubwoko bw'usaba: umuntu ku giti cye, ikigo, koreporasiyo, NGO, FBO, cyangwa ikindi"),
        Step(service_id=mutuelle.id, step_no=3, instruction="Download the household template", instruction_rw="Manura urupapuro rw'umuryango"),
        Step(service_id=mutuelle.id, step_no=4, instruction="Fill in the household details (ID numbers and amount for each person) and select the coverage year", instruction_rw="Uzuza amakuru y'umuryango (indangamuntu n'amafaranga ya buri wese) uhitemo umwaka"),
        Step(service_id=mutuelle.id, step_no=5, instruction="Upload the filled template, review the summary, and proceed to payment", instruction_rw="Ohereza urupapuro rwuzuye, urebe incamake, hanyuma ukomeze kwishyura"),

        Step(service_id=driving_license.id, step_no=1, instruction="Register for and pass the Provisional Theory Test (Rwf 5,000)", instruction_rw="Iyandikishe kandi utsinde ikizamini cy'amategeko (5,000 Rwf)"),
        Step(service_id=driving_license.id, step_no=2, instruction="Apply for and download your e-Provisional Driving License (Rwf 10,000)", instruction_rw="Saba kandi ukurure uruhushya rw'agateganyo (10,000 Rwf)"),
        Step(service_id=driving_license.id, step_no=3, instruction="Complete driving school training", instruction_rw="Rangiza amasomo yo kwiga gutwara imodoka"),
        Step(service_id=driving_license.id, step_no=4, instruction="Register for and pass the Definitive (practical) Driving Test (Rwf 10,000)", instruction_rw="Iyandikishe kandi utsinde ikizamini cy'imyitozo (10,000 Rwf)"),
        Step(service_id=driving_license.id, step_no=5, instruction="Apply for your Definitive Driving License (Rwf 50,000, processed in 14 days)", instruction_rw="Saba uruhushya rwemewe burundu (50,000 Rwf, mu minsi 14)"),
    ]

    for step in steps:
        db.add(step)
    db.commit()
    logger.info(f"Seeded {len(steps)} steps")
    return steps


def seed_conversations(db, users):
    conversations = [
        Conversation(user_id=users[0].id, status="completed"),
        Conversation(user_id=users[1].id, status="active"),
    ]
    for conversation in conversations:
        db.add(conversation)
    db.commit()
    logger.info(f"Seeded {len(conversations)} conversations")
    return conversations


def seed_messages(db, conversations):
    messages = [
        Message(conversation_id=conversations[0].id, role="user", content="Nshaka gusaba indangamuntu", input_type="text"),
        Message(conversation_id=conversations[0].id, role="assistant", content="Nzakufasha gusaba indangamuntu. Ibikenewe ni ibi...", input_type="text"),
        Message(conversation_id=conversations[1].id, role="user", content="Nshaka icyemezo cy'amavuko", input_type="voice"),
        Message(conversation_id=conversations[1].id, role="assistant", content="Nzakufasha kubona icyemezo cy'amavuko...", input_type="text"),
    ]
    for message in messages:
        db.add(message)
    db.commit()
    logger.info(f"Seeded {len(messages)} messages")
    return messages


def seed_applications(db, users, services):
    national_id = services[0]
    birth_cert = services[2]

    applications = [
        Application(user_id=users[0].id, service_id=national_id.id, status="submitted", reference_number="GOV-2026-00001"),
        Application(user_id=users[1].id, service_id=birth_cert.id, status="draft", reference_number="GOV-2026-00002"),
    ]
    for application in applications:
        db.add(application)
    db.commit()
    logger.info(f"Seeded {len(applications)} applications")
    return applications


def seed_application_data(db, applications, requirements):
    national_id_app = applications[0]
    birth_cert_app = applications[1]

    application_data = [
        ApplicationData(application_id=national_id_app.id, requirement_id=requirements[0].id, value="Self"),
        ApplicationData(application_id=national_id_app.id, requirement_id=requirements[1].id, value="CID-2024-00456"),
        ApplicationData(application_id=national_id_app.id, requirement_id=requirements[2].id, value="Nyarugenge"),
        ApplicationData(application_id=birth_cert_app.id, requirement_id=requirements[20].id, value="Self"),
        ApplicationData(application_id=birth_cert_app.id, requirement_id=requirements[21].id, value="Kigali"),
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
