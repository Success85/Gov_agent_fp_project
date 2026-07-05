from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship, validates
from datetime import datetime, timezone
import re
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    preferred_language = Column(String(10), nullable=False, default="rw")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    conversations = relationship("Conversation", back_populates="user")

    @validates("phone_number")
    def validate_phone_number(self, key, phone):
        # Strip whitespace
        phone = phone.strip()

        if not phone:
            raise ValueError("Phone number cannot be empty")

        cleaned = re.sub(r"[\s\-]", "", phone)

        pattern = r"^(\+?250|0)7[2389]\d{7}$"
        if not re.match(pattern, cleaned):
            raise ValueError(
                f"Invalid phone number format: {phone}. "
                "Expected Rwandan format: 07XXXXXXXX or +2507XXXXXXXX"
            )

        if cleaned.startswith("+250"):
            cleaned = "0" + cleaned[4:]
        elif cleaned.startswith("250"):
            cleaned = "0" + cleaned[3:]

        return cleaned

    @validates("preferred_language")
    def validate_language(self, key, language):
        language = language.strip().lower()

        allowed = ["rw", "en", "fr"]
        if language not in allowed:
            raise ValueError(
                f"Invalid language: {language}. "
                f"Allowed values are: rw (Kinyarwanda), en (English), fr (French)"
            )
        return language

    def __repr__(self):
        return f"<User id={self.id} phone={self.phone_number}>"
