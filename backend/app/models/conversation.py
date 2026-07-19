from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship, validates
from datetime import datetime, timezone
from app.db.base import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    status = Column(String(20), nullable=False, default="active")
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    ended_at = Column(DateTime, nullable=True)

    # Application-flow state tracking
    pending_service_id = Column(Integer, ForeignKey("services.id"), nullable=True)
    awaiting_requirement_id = Column(Integer, ForeignKey("requirements.id"), nullable=True)
    awaiting_payment_confirmation = Column(Boolean, nullable=False, default=False)

    # Relationships
    user = relationship("User", back_populates="conversations")
    application = relationship("Application", back_populates="conversation", uselist=False)
    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan"
    )

    @validates("status")
    def validate_status(self, key, status):
        status = status.strip().lower()
        allowed = ["active", "completed", "abandoned"]
        if status not in allowed:
            raise ValueError(
                f"Invalid status: {status}. "
                f"Allowed values are: {allowed}"
            )
        return status

    def __repr__(self):
        return (
            f"<Conversation id={self.id} "
            f"user_id={self.user_id} "
            f"status={self.status}>"
        )