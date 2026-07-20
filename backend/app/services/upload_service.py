import logging
import os
from pathlib import Path
from sqlalchemy.orm import Session
from app.models.upload import Upload

logger = logging.getLogger(__name__)

# Storage folder for uploaded files
UPLOAD_BASE_DIR = Path("storage/uploads")


def get_upload_dir(application_id: int) -> Path:
    
    upload_dir = UPLOAD_BASE_DIR / str(application_id)
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


def create_upload(
    application_id: int,
    file_name: str,
    file_path: str,
    file_type: str,
    db: Session,
    requirement_id: int = None,
    file_size_kb: int = None
) -> Upload:
   
    try:
        upload = Upload(
            application_id=application_id,
            requirement_id=requirement_id,
            file_path=file_path,
            file_name=file_name,
            file_type=file_type,
            file_size_kb=file_size_kb
        )
        db.add(upload)
        db.commit()
        db.refresh(upload)
        logger.info(
            f"Upload record created id={upload.id} "
            f"application_id={application_id} "
            f"file={file_name}"
        )
        return upload

    except Exception as e:
        db.rollback()
        logger.error(f"Error creating upload record: {e}")
        raise


def get_uploads_by_application(
    application_id: int,
    db: Session
) -> list[Upload]:
    
    try:
        uploads = db.query(Upload).filter(
            Upload.application_id == application_id
        ).order_by(
            Upload.uploaded_at.asc()
        ).all()

        logger.info(
            f"Found {len(uploads)} uploads "
            f"for application_id={application_id}"
        )
        return uploads

    except Exception as e:
        logger.error(f"Error fetching uploads: {e}")
        raise


def get_upload_by_id(
    upload_id: int,
    db: Session
) -> Upload | None:
   
    try:
        upload = db.query(Upload).filter(
            Upload.id == upload_id
        ).first()

        if not upload:
            logger.info(f"No upload found with id={upload_id}")
        return upload

    except Exception as e:
        logger.error(f"Error fetching upload: {e}")
        raise


def get_uploads_by_requirement(
    application_id: int,
    requirement_id: int,
    db: Session
) -> list[Upload]:
    
    try:
        uploads = db.query(Upload).filter(
            Upload.application_id == application_id,
            Upload.requirement_id == requirement_id
        ).all()

        return uploads

    except Exception as e:
        logger.error(f"Error fetching uploads by requirement: {e}")
        raise


def delete_upload(
    upload_id: int,
    db: Session
) -> bool:
   
    try:
        upload = get_upload_by_id(upload_id=upload_id, db=db)

        if not upload:
            logger.warning(
                f"Cannot delete — upload id={upload_id} not found"
            )
            return False

        # Delete file from disk first
        file_path = Path(upload.file_path)
        if file_path.exists():
            file_path.unlink()
            logger.info(f"Deleted file from disk: {upload.file_path}")
        else:
            logger.warning(
                f"File not found on disk: {upload.file_path}"
            )

        # Delete database record
        db.delete(upload)
        db.commit()
        logger.info(f"Upload record deleted id={upload_id}")
        return True

    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting upload: {e}")
        raise


def check_required_uploads_complete(
    application_id: int,
    service_id: int,
    db: Session
) -> dict:
    
    try:
        from app.services.service_data import get_requirements_by_service_id

        all_requirements = get_requirements_by_service_id(
            service_id=service_id,
            db=db
        )

        upload_requirements = [
            r for r in all_requirements
            if r.needs_upload and r.is_mandatory
        ]

        complete = []
        missing = []

        for req in upload_requirements:
            uploads = get_uploads_by_requirement(
                application_id=application_id,
                requirement_id=req.id,
                db=db
            )
            if uploads:
                complete.append({
                    "requirement_id": req.id,
                    "name": req.name,
                    "name_rw": req.name_rw
                })
            else:
                missing.append({
                    "requirement_id": req.id,
                    "name": req.name,
                    "name_rw": req.name_rw
                })

        result = {
            "all_complete": len(missing) == 0,
            "complete": complete,
            "missing": missing,
            "total_required": len(upload_requirements),
            "total_complete": len(complete)
        }

        logger.info(
            f"Upload check for application_id={application_id}: "
            f"{len(complete)}/{len(upload_requirements)} complete"
        )
        return result

    except Exception as e:
        logger.error(f"Error checking required uploads: {e}")
        raise