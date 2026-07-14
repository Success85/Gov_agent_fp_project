from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.service import Service
from app.schemas import ServiceDetailRead, ServiceRead
from app.services.flow_manager import get_service_overview, list_services

router = APIRouter(prefix="/services", tags=["services"])


@router.get("", response_model=list[ServiceRead])
def get_services(db: Session = Depends(get_db)):
    return list_services(db)


@router.get("/{service_id}", response_model=ServiceDetailRead)
def get_service(service_id: int, db: Session = Depends(get_db)):
    service = db.get(Service, service_id)
    if service is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")

    overview = get_service_overview(db, service_id)
    return ServiceDetailRead(
        id=service.id,
        name=service.name,
        name_rw=service.name_rw,
        category=service.category,
        description=service.description,
        fee=float(service.fee),
        processing_days=service.processing_days,
        requirements=overview["requirements"],
        steps=overview["steps"],
    )
