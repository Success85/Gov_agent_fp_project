from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.application import Application, PaymentTransaction
from app.schemas import PaymentCreate, PaymentRead, FlutterwaveVerifyRequest
from app.services.payment import simulate_momo_payment
from app.services.flutterwave import verify_transaction, FlutterwaveVerificationError
from app.services.flow_manager import generate_approval_document, build_closing_message, add_message

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

    closing_message = None
    document_id = None

    if simulated.status == "success":
        application.status = "submitted"
        db.add(application)
        db.commit()
        db.refresh(transaction)
        db.refresh(application)

        document = generate_approval_document(db, application)
        document_id = document.id

        language = payload.language or (application.user.preferred_language if application.user else "en")
        closing_message = build_closing_message(db, application, transaction.gateway_reference, language=language)

        if application.conversation_id:
            add_message(db, application.conversation_id, "assistant", closing_message)
    else:
        db.commit()
        db.refresh(transaction)

    return PaymentRead(
        id=transaction.id,
        application_id=transaction.application_id,
        payment_method=transaction.payment_method,
        gateway_reference=transaction.gateway_reference,
        amount=float(transaction.amount),
        status=transaction.status,
        created_at=transaction.created_at,
        closing_message=closing_message,
        document_id=document_id,
    )


@router.post("/{application_id}/verify-flutterwave", response_model=PaymentRead, status_code=status.HTTP_201_CREATED)
def verify_flutterwave_payment(application_id: int, payload: FlutterwaveVerifyRequest, db: Session = Depends(get_db)):
    application = db.get(Application, application_id)
    if application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    if application.service is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Application has no linked service")

    try:
        data = verify_transaction(payload.transaction_id)
    except FlutterwaveVerificationError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Could not verify payment: {exc}")

    expected_amount = float(application.service.fee)
    verified_status = data.get("status")
    verified_amount = float(data.get("amount", 0) or 0)
    verified_currency = data.get("currency")
    verified_tx_ref = data.get("tx_ref")

    is_valid = (
        verified_status == "successful"
        and verified_tx_ref == payload.tx_ref
        and verified_currency == "RWF"
        and abs(verified_amount - expected_amount) < 0.01
    )

    transaction = PaymentTransaction(
        application_id=application_id,
        payment_method="flutterwave",
        gateway_reference=data.get("flw_ref") or payload.tx_ref,
        amount=verified_amount or expected_amount,
        status="success" if is_valid else "failed",
    )
    db.add(transaction)

    closing_message = None
    document_id = None

    if is_valid:
        application.status = "submitted"
        db.add(application)
        db.commit()
        db.refresh(transaction)
        db.refresh(application)

        document = generate_approval_document(db, application)
        document_id = document.id

        language = payload.language or (application.user.preferred_language if application.user else "en")
        closing_message = build_closing_message(db, application, transaction.gateway_reference, language=language)

        if application.conversation_id:
            add_message(db, application.conversation_id, "assistant", closing_message)
    else:
        db.commit()
        db.refresh(transaction)

    return PaymentRead(
        id=transaction.id,
        application_id=transaction.application_id,
        payment_method=transaction.payment_method,
        gateway_reference=transaction.gateway_reference,
        amount=float(transaction.amount),
        status=transaction.status,
        created_at=transaction.created_at,
        closing_message=closing_message,
        document_id=document_id,
    )
