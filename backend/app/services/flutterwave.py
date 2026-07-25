from __future__ import annotations

import requests

from app.core.config import get_settings


class FlutterwaveVerificationError(Exception):
    pass


def verify_transaction(transaction_id: str) -> dict:
    """
    Calls Flutterwave's server-side Verify Transaction endpoint using the
    SECRET key. This must always be used to confirm a payment - the
    client-side checkout callback alone is never sufficient, since it can
    be spoofed or intercepted.
    """
    settings = get_settings()
    if not settings.flutterwave_secret_key:
        raise FlutterwaveVerificationError("Flutterwave secret key is not configured")

    url = f"https://api.flutterwave.com/v3/transactions/{transaction_id}/verify"
    headers = {"Authorization": f"Bearer {settings.flutterwave_secret_key}"}

    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    payload = response.json()

    if payload.get("status") != "success":
        raise FlutterwaveVerificationError(f"Flutterwave verification request failed: {payload}")

    return payload.get("data", {})
