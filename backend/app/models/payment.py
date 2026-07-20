from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship, validates
from datetime import datetime, timezone
from app.db.base import Base


VALID_PAYMENT_STATUSES = ["pending", "confirmed", "failed"]


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(
        Integer,
        ForeignKey("applications.id"),
        nullable=False,
        unique=True,
        index=True
    )
    transaction_reference = Column(String(100), nullable=False, unique=True)
    proof_reference = Column(String(255), nullable=True)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    paid_at = Column(DateTime, nullable=True)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    application = relationship(
        "Application",
        back_populates="payment"
    )

    @validates("status")
    def validate_status(self, key, status):
        status = status.strip().lower()
        if status not in VALID_PAYMENT_STATUSES:
            raise ValueError(
                f"Invalid payment status: {status}. "
                f"Allowed values are: {VALID_PAYMENT_STATUSES}"
            )
        return status

    @validates("amount")
    def validate_amount(self, key, amount):
        if amount <= 0:
            raise ValueError(
                "Payment amount must be greater than zero"
            )
        return amount

    @validates("transaction_reference")
    def validate_transaction_reference(self, key, transaction_reference):
        transaction_reference = transaction_reference.strip()
        if not transaction_reference:
            raise ValueError("Transaction reference cannot be empty")
        return transaction_reference

    def __repr__(self):
      return (
        f"<Payment id={self.id} "
        f"application_id={self.application_id} "
        f"amount={self.amount} "
        f"status={self.status}>"
    )