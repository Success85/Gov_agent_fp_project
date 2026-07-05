from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship, validates
from datetime import datetime, timezone
from app.db.base import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(
        Integer,
        ForeignKey("conversations.id"),
        nullable=False,
        index=True
    )
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    input_type = Column(String(10), nullable=False, default="text")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

    @validates("role")
    def validate_role(self, key, role):
        role = role.strip().lower()
        allowed = ["user", "assistant", "system"]
        if role not in allowed:
            raise ValueError(
                f"Invalid role: {role}. "
                f"Allowed values are: {allowed}"
            )
        return role

    @validates("input_type")
    def validate_input_type(self, key, input_type):
        input_type = input_type.strip().lower()
        allowed = ["text", "voice"]
        if input_type not in allowed:
            raise ValueError(
                f"Invalid input type: {input_type}. "
                f"Allowed values are: text or voice"
            )
        return input_type

    @validates("content")
    def validate_content(self, key, content):
        content = content.strip()
        if not content:
            raise ValueError("Message content cannot be empty")
        return content

    def __repr__(self):
        return (
            f"<Message id={self.id} "
            f"conversation_id={self.conversation_id} "
            f"role={self.role} "
            f"input_type={self.input_type}>"
        )