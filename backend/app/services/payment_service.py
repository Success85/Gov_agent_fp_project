import logging
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.payment import Payment

logger = logging.getLogger(__name__)

VALID_PAYMENT_TRANSITIONS = {
    "pending": ["confirmed", "failed"],
    "confirmed": [],
    "failed": ["pending"]
}


def generate_transaction_reference() -> str:
   
    unique_id = str(uuid.uuid4())[:8].upper()
    return f"FLW-{unique_id}"


def create_payment(
    application_id: int,
    amount: float,
    db: Session
) -> Payment:
   
    try:
        existing = get_payment_by_application(
            application_id=application_id,
            db=db
        )

        if existing:
            raise ValueError(
                f"Payment already exists for "
                f"application_id={application_id}. "
                f"Use update_payment_status() to update it."
            )

        transaction_reference = generate_transaction_reference()

        payment = Payment(
            application_id=application_id,
            transaction_reference=transaction_reference,
            amount=amount,
            status="pending"
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)
        logger.info(
            f"Payment created id={payment.id} "
            f"application_id={application_id} "
            f"amount={amount} "
            f"reference={transaction_reference}"
        )
        return payment

    except ValueError:
        raise

    except Exception as e:
        db.rollback()
        logger.error(f"Error creating payment: {e}")
        raise


def get_payment_by_application(
    application_id: int,
    db: Session
) -> Payment | None:
    
    try:
        payment = db.query(Payment).filter(
            Payment.application_id == application_id
        ).first()

        return payment

    except Exception as e:
        logger.error(f"Error fetching payment: {e}")
        raise


def get_payment_by_id(
    payment_id: int,
    db: Session
) -> Payment | None:
    
    try:
        payment = db.query(Payment).filter(
            Payment.id == payment_id
        ).first()

        if not payment:
            logger.info(f"No payment found with id={payment_id}")
        return payment

    except Exception as e:
        logger.error(f"Error fetching payment by id: {e}")
        raise


def update_payment_status(
    application_id: int,
    status: str,
    db: Session,
    proof_reference: str = None
) -> Payment | None:
    
    try:
        payment = get_payment_by_application(
            application_id=application_id,
            db=db
        )

        if not payment:
            raise ValueError(
                f"No payment found for "
                f"application_id={application_id}"
            )

        current_status = payment.status
        allowed_next = VALID_PAYMENT_TRANSITIONS.get(
            current_status, []
        )

        if status not in allowed_next:
            raise ValueError(
                f"Invalid payment status transition. "
                f"Cannot move from '{current_status}' to '{status}'. "
                f"Allowed transitions: "
                f"{allowed_next if allowed_next else 'none'}"
            )

        payment.status = status

        if status == "confirmed":
            payment.paid_at = datetime.now(timezone.utc)
            if proof_reference:
                payment.proof_reference = proof_reference

        db.commit()
        db.refresh(payment)
        logger.info(
            f"Payment id={payment.id} "
            f"transitioned from {current_status} to {status}"
        )
        return payment

    except ValueError:
        raise

    except Exception as e:
        db.rollback()
        logger.error(f"Error updating payment status: {e}")
        raise


def get_payment_summary(
    application_id: int,
    db: Session
) -> dict:
    
    try:
        payment = get_payment_by_application(
            application_id=application_id,
            db=db
        )

        if not payment:
            return {
                "payment_exists": False,
                "application_id": application_id
            }

        return {
            "payment_exists": True,
            "payment_id": payment.id,
            "application_id": application_id,
            "transaction_reference": payment.transaction_reference,
            "amount": str(payment.amount),
            "status": payment.status,
            "proof_reference": payment.proof_reference,
            "paid_at": str(payment.paid_at) if payment.paid_at else None,
            "created_at": str(payment.created_at)
        }

    except Exception as e:
        logger.error(f"Error fetching payment summary: {e}")
        raise