from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.application import Application
from app.schemas import ApplicationCreate, ApplicationDataUpsert, ApplicationRead
from app.services.flow_manager import start_application, upsert_application_data

router = APIRouter(prefix="/applications", tags=["applications"])


@router.post("", response_model=ApplicationRead, status_code=status.HTTP_201_CREATED)
def create_application(payload: ApplicationCreate, db: Session = Depends(get_db)):
    try:
        return start_application(db, payload.user_id, payload.service_id, payload.conversation_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/{application_id}", response_model=ApplicationRead)
def get_application(application_id: int, db: Session = Depends(get_db)):
    application = db.get(Application, application_id)
    if application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    return application


@router.put("/{application_id}/data/{requirement_id}")
def store_application_data(application_id: int, requirement_id: int, payload: ApplicationDataUpsert, db: Session = Depends(get_db)):
    return upsert_application_data(db, application_id, requirement_id, payload.value)
