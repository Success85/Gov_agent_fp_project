from __future__ import annotations

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from pathlib import Path

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def send_approval_email(
    to_email: str,
    applicant_name: str | None,
    service_name: str,
    reference_number: str,
    gateway_reference: str,
    fee: float,
    collection_location: str | None,
    closing_message: str,
    language: str = "en",
    document_path: str | None = None,
) -> bool:
    """
    Sends a real confirmation email via Gmail SMTP once an application has
    been successfully paid for. Returns True on success, False otherwise
    (never raises - a failed email should never break the payment flow).
    """
    settings = get_settings()
    if not settings.gmail_address or not settings.gmail_app_password:
        logger.warning("Gmail credentials not configured; skipping approval email")
        return False

    name_display = applicant_name or ("Umukiriya" if language == "rw" else "Applicant")
    subject = (
        f"GovAgent - Ubusabe bwawe bwemejwe: {service_name}"
        if language == "rw"
        else f"GovAgent - Your {service_name} application is approved"
    )

    collection_line = collection_location or ("Reba imeyili yawe" if language == "rw" else "Check your email for details")

    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #1a1a1a; line-height: 1.6;">
        <div style="max-width: 560px; margin: 0 auto; padding: 24px; border: 1px solid #e0e0e0; border-radius: 8px;">
          <h2 style="color: #0057b7;">GovAgent</h2>
          <p>{"Muraho" if language == "rw" else "Hello"} {name_display},</p>
          <p>{closing_message.replace(chr(10), '<br>')}</p>
          <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 20px 0;">
          <table style="width: 100%; font-size: 14px;">
            <tr><td style="padding: 4px 0;"><strong>{"Serivisi" if language == "rw" else "Service"}</strong></td><td>{service_name}</td></tr>
            <tr><td style="padding: 4px 0;"><strong>{"Nomero y'Ubusabe" if language == "rw" else "Application Reference"}</strong></td><td>{reference_number}</td></tr>
            <tr><td style="padding: 4px 0;"><strong>{"Nomero y'Ubwishyu" if language == "rw" else "Payment Reference"}</strong></td><td>{gateway_reference}</td></tr>
            <tr><td style="padding: 4px 0;"><strong>{"Amafaranga" if language == "rw" else "Fee Paid"}</strong></td><td>{fee:.2f} RWF</td></tr>
            <tr><td style="padding: 4px 0;"><strong>{"Aho gukuriramo" if language == "rw" else "Collection Location"}</strong></td><td>{collection_line}</td></tr>
          </table>
          <p style="margin-top: 20px;">
            {"Iyi ni inyandiko yemewe. Ushobora kuyisohora (print) cyangwa ukajya ku biro byavuzwe hejuru kugira ngo ubone inyandiko yawe."
              if language == "rw"
              else "This is your official confirmation. You may print this email as a hard copy, or visit the collection office listed above to receive your document."}
          </p>
          <p style="color: #666; font-size: 12px; margin-top: 24px;">GovAgent &mdash; Irembo Service Assistant</p>
        </div>
      </body>
    </html>
    """

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = settings.gmail_address
    message["To"] = to_email
    message.attach(MIMEText(html_body, "html"))

    if document_path:
        doc_file = Path(document_path)
        if doc_file.exists():
            with open(doc_file, "rb") as f:
                attachment = MIMEApplication(f.read(), _subtype="pdf")
                attachment.add_header("Content-Disposition", "attachment", filename=doc_file.name)
                message.attach(attachment)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=15) as server:
            server.starttls()
            server.login(settings.gmail_address, settings.gmail_app_password)
            server.sendmail(settings.gmail_address, to_email, message.as_string())
        logger.info(f"Approval email sent to {to_email}")
        return True
    except Exception as exc:
        logger.error(f"Failed to send approval email to {to_email}: {exc}")
        return False
