from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship, validates
from datetime import datetime, timezone
from app.db.database import Base


class Requirement(Base):
    __tablename__ = "requirements"

    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    name_rw = Column(String(255), nullable=False)
    is_mandatory = Column(Boolean, nullable=False, default=True)
    needs_upload = Column(Boolean, nullable=False, default=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    service = relationship("Service", back_populates="requirements")
    uploads = relationship("Upload", back_populates="requirement")

    @validates("name")
    def validate_name(self, key, name):
        name = name.strip()
        if not name:
            raise ValueError("Requirement name cannot be empty")
        return name

    @validates("name_rw")
    def validate_name_rw(self, key, name_rw):
        name_rw = name_rw.strip()
        if not name_rw:
            raise ValueError("Kinyarwanda requirement name cannot be empty")
        return name_rw

    def __repr__(self):
        return (
            f"<Requirement id={self.id} "
            f"service_id={self.service_id} "
            f"name={self.name} "
            f"mandatory={self.is_mandatory}>"
        )