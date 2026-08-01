from tests.conftest import unique_phone
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)



def start_conversation(message: str, language: str = "en"):
    response = client.post(
        "/chat",
        json={"phone_number": unique_phone(), "message": message, "preferred_language": language},
    )
    body = response.json()
    return body["conversation_id"], body["user_id"]


def send(conversation_id: int, user_id: int, message: str, language: str = "en"):
    response = client.post(
        "/chat",
        json={
            "user_id": user_id,
            "conversation_id": conversation_id,
            "message": message,
            "preferred_language": language,
        },
    )
    return response.json()


def test_national_id_full_requirement_collection() -> None:
    conv_id, user_id = start_conversation("national id")
    send(conv_id, user_id, "yes")
    send(conv_id, user_id, "Test Applicant")  # full name
    send(conv_id, user_id, "Self")
    send(conv_id, user_id, "CID-TEST-001")
    send(conv_id, user_id, "Kimironko")
    send(conv_id, user_id, "2026-09-01")
    send(conv_id, user_id, "Gasabo")  # real district, should be accepted
    result = send(conv_id, user_id, "Kimironko")

    assert result["intent"] == "awaiting_payment_confirmation"
    assert "Test Applicant" in result["assistant_message"]
    assert result["fee"] == 500.0


def test_invalid_district_is_rejected() -> None:
    conv_id, user_id = start_conversation("national id")
    send(conv_id, user_id, "yes")
    send(conv_id, user_id, "Test Applicant")
    send(conv_id, user_id, "Self")
    send(conv_id, user_id, "CID-TEST-002")
    send(conv_id, user_id, "Kimironko")
    send(conv_id, user_id, "2026-09-01")
    result = send(conv_id, user_id, "NotARealDistrict")

    assert "district" in result["assistant_message"].lower()
    assert result["intent"] == "collecting_requirements"  # still stuck on the same field


def test_mutuelle_skips_org_name_for_individual() -> None:
    conv_id, user_id = start_conversation("mutuelle renewal")
    send(conv_id, user_id, "yes")
    send(conv_id, user_id, "Test Applicant")
    send(conv_id, user_id, "Single")
    result = send(conv_id, user_id, "Individual")

    # Should skip straight to Coverage Year, never asking for Org Name/TIN
    assert "Coverage Year" in result["assistant_message"]
    assert "Organization" not in result["assistant_message"]


def test_mutuelle_requires_org_name_for_company() -> None:
    conv_id, user_id = start_conversation("mutuelle renewal")
    send(conv_id, user_id, "yes")
    send(conv_id, user_id, "Test Applicant")
    send(conv_id, user_id, "Single")
    result = send(conv_id, user_id, "Company")

    assert "Organization Name" in result["assistant_message"]


def test_marriage_date_must_be_21_days_out() -> None:
    conv_id, user_id = start_conversation("declare a marriage")
    send(conv_id, user_id, "yes")
    send(conv_id, user_id, "Test Applicant")
    send(conv_id, user_id, "Rwanda")
    too_soon = send(conv_id, user_id, "2026-08-05")

    assert "21 days" in too_soon["assistant_message"]
    assert too_soon["intent"] == "collecting_requirements"
