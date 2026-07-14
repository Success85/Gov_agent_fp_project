from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, validates
from datetime import datetime, timezone
import uuid
from app.db.base import Base


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False, index=True)
    status = Column(String(20), nullable=False, default="in_progress")
    reference_number = Column(String(50), unique=True, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime,
                        default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="applications")
    service = relationship("Service", back_populates="applications")
    application_data = relationship(
        "ApplicationData",
        back_populates="application",
        cascade="all, delete-orphan"
    )

    @validates("status")
    def validate_status(self, key, status):
        status = status.strip().lower()
        allowed = ["in_progress", "submitted", "completed", "cancelled"]
        if status not in allowed:
            raise ValueError(
                f"Invalid status: {status}. "
                f"Allowed values are: {allowed}"
            )
        return status

    @validates("reference_number")
    def validate_reference_number(self, key, reference_number):
        if reference_number is not None:
            reference_number = reference_number.strip().upper()
        return reference_number

    def generate_reference_number(self):
        """
        Generate a unique reference number for this application.
        Format: GOV-YYYY-XXXXX
        Example: GOV-2026-00001
        """
        year = datetime.now(timezone.utc).year
        unique = str(uuid.uuid4())[:5].upper()
        return f"GOV-{year}-{unique}"

    def __repr__(self):
        return (
            f"<Application id={self.id} "
            f"user_id={self.user_id} "
            f"service_id={self.service_id} "
            f"status={self.status}>"
        )


class ApplicationData(Base):
    __tablename__ = "application_data"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(
        Integer,
        ForeignKey("applications.id"),
        nullable=False,
        index=True
    )
    field_name = Column(String(100), nullable=False)
    field_value = Column(String(500), nullable=False)

    # Unique constraint — one answer per field per application
    __table_args__ = (
        UniqueConstraint(
            "application_id",
            "field_name",
            name="uq_application_field"
        ),
    )

    # Relationships
    application = relationship("Application", back_populates="application_data")

    @validates("field_name")
    def validate_field_name(self, key, field_name):
        field_name = field_name.strip().lower()
        if not field_name:
            raise ValueError("Field name cannot be empty")
        return field_name

    @validates("field_value")
    def validate_field_value(self, key, field_value):
        field_value = field_value.strip()
        if not field_value:
            raise ValueError("Field value cannot be empty")
        return field_value

    def __repr__(self):
        return (
            f"<ApplicationData id={self.id} "
            f"application_id={self.application_id} "
            f"field={self.field_name}: {self.field_value}>"
        )
