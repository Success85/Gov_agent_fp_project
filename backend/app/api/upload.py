from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.database import get_db
from app.models.application import UploadedDocument

router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.post("/{application_id}", status_code=status.HTTP_201_CREATED)
def upload_document(
    application_id: int,
    file: UploadFile = File(...),
    requirement_id: int | None = Form(default=None),
    db: Session = Depends(get_db),
):
    settings = get_settings()
    storage_root = Path(settings.storage_dir)
    storage_root.mkdir(parents=True, exist_ok=True)

    destination_name = f"{uuid4().hex}_{file.filename}"
    destination_path = storage_root / destination_name
    with destination_path.open("wb") as buffer:
        buffer.write(file.file.read())

    record = UploadedDocument(
        application_id=application_id,
        requirement_id=requirement_id,
        file_path=str(destination_path),
        file_name=file.filename,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
