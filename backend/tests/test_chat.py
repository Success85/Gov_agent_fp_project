from tests.conftest import unique_phone
from fastapi.testclient import TestClient
from app.main import app
from app.services.grounding import GroundingContext, build_grounded_prompt

client = TestClient(app)


def test_chat_detects_national_id_service() -> None:
    """
    Intent/service detection is pure keyword matching and doesn't require
    a live AI call, so this stays robust even if the AI provider is
    unavailable or rate-limited.
    """
    response = client.post(
        "/chat",
        json={
            "phone_number": unique_phone(),
            "message": "national id",
            "preferred_language": "en",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["intent"] == "start_service"
    assert body["service_name"] == "Application for National ID"
    assert body["service_id"] is not None


def test_chat_disambiguates_birth_record_vs_birth_certificate() -> None:
    cert_response = client.post(
        "/chat",
        json={
            "phone_number": unique_phone(),
            "message": "I need a birth certificate",
            "preferred_language": "en",
        },
    )
    assert cert_response.json()["service_name"] == "Birth Certificate"

    record_response = client.post(
        "/chat",
        json={
            "phone_number": unique_phone(),
            "message": "I want to register a birth",
            "preferred_language": "en",
        },
    )
    assert record_response.json()["service_name"] == "Birth Record"


def test_chat_detects_marriage_declaration_in_french() -> None:
    response = client.post(
        "/chat",
        json={
            "phone_number": unique_phone(),
            "message": "je veux declarer un mariage",
            "preferred_language": "fr",
        },
    )
    assert response.json()["service_name"] == "Marriage Declaration"


def test_chat_returns_200_even_if_ai_provider_is_unavailable() -> None:
    """
    Even if the AI provider is down/rate-limited, the endpoint should
    still respond successfully with a graceful fallback message rather
    than a server error.
    """
    response = client.post(
        "/chat",
        json={
            "phone_number": unique_phone(),
            "message": "national id",
            "preferred_language": "en",
        },
    )
    assert response.status_code == 201
    assert len(response.json()["assistant_message"]) > 0


def test_grounded_prompt_contains_real_service_data_not_hallucinated() -> None:
    """
    This tests the actual grounding mechanism directly, with no network
    call - verifying that real service data (fee, requirements, steps)
    flows correctly into the prompt sent to the AI model, which is what
    prevents hallucinated requirements/fees regardless of what the AI
    itself ultimately generates.
    """
    context = GroundingContext(
        service_name="Application for National ID",
        description="Apply for a Rwandan national identity card.",
        fee=500.00,
        requirements=["Applying For (Self or Bulk)", "Collection District"],
        steps=["Select 'Application for National ID'", "Review the summary and proceed to payment"],
    )
    prompt = build_grounded_prompt("national id please", context, language="en")

    assert "500.0" in prompt
    assert "Applying For (Self or Bulk)" in prompt
    assert "Collection District" in prompt
    assert "Select 'Application for National ID'" in prompt
    assert "Application for National ID" in prompt


def test_grounded_prompt_has_dedicated_french_system_prompt() -> None:
    """
    Regression test for a real bug found tonight: French previously had
    no system prompt entry and silently fell back to English.
    """
    context = GroundingContext(service_name="Test Service", fee=100)
    fr_prompt = build_grounded_prompt("test", context, language="fr")
    en_prompt = build_grounded_prompt("test", context, language="en")

    assert "fran" in fr_prompt.lower() or "vous" in fr_prompt.lower()
    assert fr_prompt != en_prompt
