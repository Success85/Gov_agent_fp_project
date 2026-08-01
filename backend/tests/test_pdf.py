import os
from tests.conftest import unique_phone
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import SessionLocal
from app.models.application import Application

client = TestClient(app)



def test_successful_payment_generates_real_pdf() -> None:
    phone = unique_phone()
    r = client.post("/chat", json={"phone_number": phone, "message": "national id", "preferred_language": "en"})
    conv_id = r.json()["conversation_id"]
    user_id = r.json()["user_id"]

    def send(message):
        return client.post(
            "/chat",
            json={"user_id": user_id, "conversation_id": conv_id, "message": message, "preferred_language": "en"},
        ).json()

    send("yes")
    send("PDF Test Applicant")
    send("Self")
    send("CID-PDF-TEST")
    send("Kimironko")
    send("2026-09-01")
    send("Gasabo")
    send("Kimironko")
    send("yes")
    result = send("pdf-test@example.com")
    application_id = result["application_id"]

    document_id = None
    for amount in [700, 701, 702, 703, 704, 705]:
        payment_response = client.post(
            f"/payments/{application_id}",
            json={"payment_method": "mobile_money", "amount": amount, "language": "en"},
        )
        body = payment_response.json()
        if body.get("status") == "success":
            document_id = body.get("document_id")
            break

    assert document_id is not None, "Expected a successful payment to generate a document"

    # Confirm a real PDF file was actually written to disk
    db = SessionLocal()
    try:
        application = db.get(Application, application_id)
        document = next((d for d in application.generated_documents if d.id == document_id), None)
        assert document is not None
        assert os.path.exists(document.file_path)
        assert document.file_path.endswith(".pdf")
        assert os.path.getsize(document.file_path) > 0

        with open(document.file_path, "rb") as f:
            header = f.read(5)
        assert header == b"%PDF-", "File should be a real PDF (correct magic bytes)"
    finally:
        db.close()
