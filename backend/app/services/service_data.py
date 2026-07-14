import logging
from sqlalchemy.orm import Session
from app.models.service import Service
from app.models.requirement import Requirement
from app.models.steps import Step

logger = logging.getLogger(__name__)


def get_all_services(db: Session) -> list[Service]:
    """
    Fetch all available government services.
    Used by the frontend to display the service catalogue.
    """
    try:
        services = db.query(Service).order_by(
            Service.category.asc(),
            Service.name.asc()
        ).all()

        logger.info(f"Found {len(services)} services")
        return services

    except Exception as e:
        logger.error(f"Error fetching all services: {e}")
        raise


def get_service_by_id(
    service_id: int,
    db: Session
) -> Service | None:
    """
    Fetch a single service by its ID.
    Returns None if not found.
    """
    try:
        service = db.query(Service).filter(
            Service.id == service_id
        ).first()

        if not service:
            logger.info(f"No service found with id={service_id}")
        return service

    except Exception as e:
        logger.error(f"Error fetching service by id: {e}")
        raise


def get_service_by_name(
    name: str,
    db: Session
) -> Service | None:
    """
    Fetch a service by its English name.
    Case insensitive search.
    """
    try:
        service = db.query(Service).filter(
            Service.name.ilike(f"%{name}%")
        ).first()

        return service

    except Exception as e:
        logger.error(f"Error fetching service by name: {e}")
        raise


def get_services_by_category(
    category: str,
    db: Session
) -> list[Service]:
    """
    Fetch all services in a specific category.
    Used by frontend to filter services by category.
    """
    try:
        services = db.query(Service).filter(
            Service.category == category.strip().title()
        ).order_by(
            Service.name.asc()
        ).all()

        logger.info(
            f"Found {len(services)} services "
            f"in category={category}"
        )
        return services

    except Exception as e:
        logger.error(f"Error fetching services by category: {e}")
        raise


def get_requirements_by_service_id(
    service_id: int,
    db: Session,
    mandatory_only: bool = False
) -> list[Requirement]:
    """
    Fetch all requirements for a specific service.
    This is the most important function for AI grounding —
    Davy calls this to get verified requirements before
    generating an AI response.
    Optional: fetch only mandatory requirements.
    """
    try:
        query = db.query(Requirement).filter(
            Requirement.service_id == service_id
        )

        if mandatory_only:
            query = query.filter(
                Requirement.is_mandatory == True
            )

        requirements = query.order_by(
            Requirement.is_mandatory.desc()
        ).all()

        logger.info(
            f"Found {len(requirements)} requirements "
            f"for service_id={service_id}"
        )
        return requirements

    except Exception as e:
        logger.error(f"Error fetching requirements: {e}")
        raise


def get_steps_by_service_id(
    service_id: int,
    db: Session
) -> list[Step]:
    """
    Fetch all steps for a specific service.
    Ordered by step_no so AI guides citizen
    through steps in the correct sequence.
    """
    try:
        steps = db.query(Step).filter(
            Step.service_id == service_id
        ).order_by(
            Step.step_no.asc()
        ).all()

        logger.info(
            f"Found {len(steps)} steps "
            f"for service_id={service_id}"
        )
        return steps

    except Exception as e:
        logger.error(f"Error fetching steps: {e}")
        raise


def get_full_service_context(
    service_id: int,
    db: Session
) -> dict:
   
    try:
        service = get_service_by_id(service_id=service_id, db=db)

        if not service:
            raise ValueError(
                f"Service with id={service_id} not found. "
                f"Cannot build grounding context for AI."
            )

        requirements = get_requirements_by_service_id(
            service_id=service_id,
            db=db
        )

        steps = get_steps_by_service_id(
            service_id=service_id,
            db=db
        )

        if not requirements:
            raise ValueError(
                f"Service id={service_id} has no requirements. "
                f"Cannot ground AI response without verified requirements."
            )

        if not steps:
            raise ValueError(
                f"Service id={service_id} has no steps. "
                f"Cannot ground AI response without verified steps."
            )

        context = {
            "service": {
                "id": service.id,
                "name": service.name,
                "name_rw": service.name_rw,
                "category": service.category,
                "description": service.description,
                "fee": str(service.fee),
                "processing_days": service.processing_days
            },
            "requirements": [
                {
                    "id": r.id,
                    "name": r.name,
                    "name_rw": r.name_rw,
                    "is_mandatory": r.is_mandatory,
                    "needs_upload": r.needs_upload
                }
                for r in requirements
            ],
            "steps": [
                {
                    "step_no": s.step_no,
                    "instruction": s.instruction,
                    "instruction_rw": s.instruction_rw
                }
                for s in steps
            ]
        }

        logger.info(
            f"Full context retrieved for service_id={service_id} "
            f"— {len(requirements)} requirements, {len(steps)} steps"
        )
        return context

    except ValueError:
        raise

    except Exception as e:
        logger.error(f"Error fetching full service context: {e}")
        raise