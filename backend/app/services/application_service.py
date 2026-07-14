import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.application import Application, ApplicationData

logger = logging.getLogger(__name__)


def create_application(
    user_id: int,
    service_id: int,
    db: Session
) -> Application:
    
    try:
        application = Application(
            user_id=user_id,
            service_id=service_id,
            status="in_progress"
        )
        db.add(application)
        db.commit()
        db.refresh(application)
        logger.info(
            f"New application created id={application.id} "
            f"user_id={user_id} service_id={service_id}"
        )
        return application

    except Exception as e:
        db.rollback()
        logger.error(f"Error creating application: {e}")
        raise


def get_application_by_id(
    application_id: int,
    db: Session
) -> Application | None:
   
    try:
        application = db.query(Application).filter(
            Application.id == application_id
        ).first()

        if not application:
            logger.info(
                f"No application found with id={application_id}"
            )
        return application

    except Exception as e:
        logger.error(f"Error fetching application: {e}")
        raise


def get_applications_by_user(
    user_id: int,
    db: Session
) -> list[Application]:
   
   
    try:
        applications = db.query(Application).filter(
            Application.user_id == user_id
        ).order_by(
            Application.created_at.desc()
        ).all()

        logger.info(
            f"Found {len(applications)} applications "
            f"for user_id={user_id}"
        )
        return applications

    except Exception as e:
        logger.error(f"Error fetching applications: {e}")
        raise


def get_active_application(
    user_id: int,
    service_id: int,
    db: Session
) -> Application | None:
   
    try:
        application = db.query(Application).filter(
            Application.user_id == user_id,
            Application.service_id == service_id,
            Application.status == "in_progress"
        ).first()

        return application

    except Exception as e:
        logger.error(f"Error fetching active application: {e}")
        raise


def upsert_application_data(
    application_id: int,
    field_name: str,
    field_value: str,
    db: Session,
    skip_validation: bool = False
) -> ApplicationData:
   
    try:
        if not skip_validation:
            application = get_application_by_id(
                application_id=application_id,
                db=db
            )

            if not application:
                raise ValueError(
                    f"Application id={application_id} not found."
                )

            from app.services.service_data import (
                get_requirements_by_service_id
            )
            requirements = get_requirements_by_service_id(
                service_id=application.service_id,
                db=db
            )

            valid_field_names = [
                r.name.strip().lower()
                for r in requirements
            ]

            cleaned_field_name = field_name.strip().lower()

            if cleaned_field_name not in valid_field_names:
                raise ValueError(
                    f"Invalid field '{field_name}' for "
                    f"application id={application_id}. "
                    f"Valid fields for this service are: "
                    f"{valid_field_names}"
                )

        existing = db.query(ApplicationData).filter(
            ApplicationData.application_id == application_id,
            ApplicationData.field_name == field_name.strip().lower()
        ).first()

        if existing:
            existing.field_value = field_value.strip()
            db.commit()
            db.refresh(existing)
            logger.info(
                f"Updated field '{field_name}' "
                f"for application_id={application_id}"
            )
            return existing

        new_data = ApplicationData(
            application_id=application_id,
            field_name=field_name.strip().lower(),
            field_value=field_value.strip()
        )
        db.add(new_data)
        db.commit()
        db.refresh(new_data)
        logger.info(
            f"Created field '{field_name}' "
            f"for application_id={application_id}"
        )
        return new_data

    except ValueError:
        raise

    except Exception as e:
        db.rollback()
        logger.error(f"Error upserting application data: {e}")
        raise

def get_application_data(
    application_id: int,
    db: Session
) -> list[ApplicationData]:
    
    try:
        data = db.query(ApplicationData).filter(
            ApplicationData.application_id == application_id
        ).all()

        logger.info(
            f"Found {len(data)} answered fields "
            f"for application_id={application_id}"
        )
        return data

    except Exception as e:
        logger.error(f"Error fetching application data: {e}")
        raise


def get_answered_field_names(
    application_id: int,
    db: Session
) -> list[str]:
   
    try:
        data = get_application_data(
            application_id=application_id,
            db=db
        )
        return [d.field_name for d in data]

    except Exception as e:
        logger.error(f"Error fetching answered field names: {e}")
        raise


VALID_TRANSITIONS = {
    "in_progress": ["submitted", "cancelled"],
    "submitted": ["completed", "cancelled"],
    "completed": [],
    "cancelled": []
}


def update_application_status(
    application_id: int,
    status: str,
    db: Session,
    reference_number: str = None
) -> Application | None:
   
    try:
        application = get_application_by_id(
            application_id=application_id,
            db=db
        )

        if not application:
            logger.warning(
                f"Cannot update status — "
                f"application id={application_id} not found"
            )
            return None

        current_status = application.status
        allowed_next = VALID_TRANSITIONS.get(current_status, [])

        if status not in allowed_next:
            raise ValueError(
                f"Invalid status transition for "
                f"application id={application_id}. "
                f"Cannot move from '{current_status}' to '{status}'. "
                f"Allowed transitions from '{current_status}': "
                f"{allowed_next if allowed_next else 'none — terminal state'}"
            )

        application.status = status

        if status == "submitted" and not application.reference_number:
            application.reference_number = (
                reference_number or
                application.generate_reference_number()
            )

        db.commit()
        db.refresh(application)
        logger.info(
            f"Application id={application_id} "
            f"transitioned from {current_status} to {status}. "
            f"Reference: {application.reference_number}"
        )
        return application

    except ValueError:
        raise

    except Exception as e:
        db.rollback()
        logger.error(f"Error updating application status: {e}")
        raise


def get_application_summary(
    application_id: int,
    db: Session
) -> dict:
   
    try:
        application = get_application_by_id(
            application_id=application_id,
            db=db
        )

        if not application:
            return {}

        data = get_application_data(
            application_id=application_id,
            db=db
        )

        summary = {
            "application_id": application.id,
            "service_id": application.service_id,
            "status": application.status,
            "reference_number": application.reference_number,
            "created_at": str(application.created_at),
            "updated_at": str(application.updated_at),
            "answers": {
                d.field_name: d.field_value
                for d in data
            }
        }

        logger.info(
            f"Summary retrieved for "
            f"application_id={application_id}"
        )
        return summary

    except Exception as e:
        logger.error(f"Error fetching application summary: {e}")
        raise