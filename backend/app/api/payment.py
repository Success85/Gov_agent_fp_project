from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.application import Application, PaymentTransaction
from app.schemas import PaymentCreate, PaymentRead
from app.services.payment import simulate_momo_payment

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/{application_id}", response_model=PaymentRead, status_code=status.HTTP_201_CREATED)
def create_payment(application_id: int, payload: PaymentCreate, db: Session = Depends(get_db)):
    application = db.get(Application, application_id)
    if application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    if payload.amount <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="amount must be greater than zero")

    simulated = simulate_momo_payment(
        phone_number=application.user.phone_number or "0000000000",
        amount=payload.amount,
        reference_number=application.reference_number,
    )

    transaction = PaymentTransaction(
        application_id=application_id,
        payment_method=payload.payment_method,
        gateway_reference=payload.gateway_reference or simulated.gateway_reference,
        amount=payload.amount,
        status=simulated.status,
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction
