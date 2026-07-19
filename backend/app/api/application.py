from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.application import Application
from app.models.service import Service
from app.models.user import User
from app.schemas import ApplicationCreate, ApplicationCreateByPhone, ApplicationDataUpsert, ApplicationDetailRead, ApplicationRead
from app.services.flow_manager import get_application_summary, get_or_create_user_by_phone, start_application, upsert_application_data

router = APIRouter(prefix="/applications", tags=["applications"])


@router.post("/start", response_model=ApplicationRead, status_code=status.HTTP_201_CREATED)
def start_application_by_phone(payload: ApplicationCreateByPhone, db: Session = Depends(get_db)):
    if payload.user_id is not None:
        user_id = payload.user_id
        user = db.get(User, user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    else:
        if payload.phone_number is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="phone_number or user_id is required")
        user = get_or_create_user_by_phone(db, payload.phone_number, preferred_language=payload.preferred_language)
        user_id = user.id

    try:
        return start_application(db, user_id, payload.service_id, payload.conversation_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("", response_model=ApplicationRead, status_code=status.HTTP_201_CREATED)
def create_application(payload: ApplicationCreate, db: Session = Depends(get_db)):
    user = db.get(User, payload.user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    try:
        return start_application(db, payload.user_id, payload.service_id, payload.conversation_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/{application_id}", response_model=ApplicationRead)
def get_application(application_id21: int, db: Session = Depends(get_db)):
    application = db.get(Application, application_id)
    if application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    return application


@router.get("/{application_id}/detail", response_model=ApplicationDetailRead)
def get_application_detail(application_id: int, db: Session = Depends(get_db)):
    application = db.get(Application, application_id)
    if application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    if application.service is None:
        application.service = db.get(Service, application.service_id)

    summary = get_application_summary(application)
    return ApplicationDetailRead(
        id=application.id,
        user_id=application.user_id,
        service_id=application.service_id,
        conversation_id=application.conversation_id,
        status=application.status,
        reference_number=application.reference_number,
        created_at=application.created_at,
        updated_at=application.updated_at,
        service_name=summary["service_name"],
        total_payments=summary["total_payments"],
        total_uploaded_files=summary["total_uploaded_files"],
    )


@router.put("/{application_id}/data/{requirement_id}")
def store_application_data(application_id: int, requirement_id: int, payload: ApplicationDataUpsert, db: Session = Depends(get_db)):
    return upsert_application_data(db, application_id, requirement_id, payload.value)
