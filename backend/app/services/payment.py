from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass
class PaymentResult:
    status: str
    gateway_reference: str
    processed_at: datetime
    message: str


def simulate_momo_payment(phone_number: str, amount: float, reference_number: str) -> PaymentResult:
    """
    Simulate a MoMo payment result for local development and testing.
    The status is derived deterministically from the inputs (so the same
    application/amount tends to behave consistently), but the gateway
    reference always includes a random component so retries never collide
    on the unique constraint.
    """
    seed = f"{phone_number}|{amount:.2f}|{reference_number}".encode("utf-8")
    digest = hashlib.sha256(seed).hexdigest()
    selector = int(digest[:2], 16) % 10

    if selector <= 6:
        status = "success"
        message = "Payment completed successfully."
    elif selector <= 8:
        status = "pending"
        message = "Payment is pending confirmation."
    else:
        status = "failed"
        message = "Payment failed. Please retry."

    unique_suffix = uuid.uuid4().hex[:8].upper()
    gateway_reference = f"MOMO-{digest[:8].upper()}-{unique_suffix}"

    return PaymentResult(status=status, gateway_reference=gateway_reference, processed_at=datetime.utcnow(), message=message)
