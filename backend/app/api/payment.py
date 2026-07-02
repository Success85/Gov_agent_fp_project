from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.application import Application, PaymentTransaction
from app.schemas import PaymentCreate, PaymentRead

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/{application_id}", response_model=PaymentRead, status_code=status.HTTP_201_CREATED)
def create_payment(application_id: int, payload: PaymentCreate, db: Session = Depends(get_db)):
    application = db.get(Application, application_id)
    if application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    transaction = PaymentTransaction(
        application_id=application_id,
        payment_method=payload.payment_method,
        gateway_reference=payload.gateway_reference,
        amount=payload.amount,
        status="pending",
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction
