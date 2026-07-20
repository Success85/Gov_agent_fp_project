from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, validates
from datetime import datetime, timezone
from app.db.base import Base


ALLOWED_FILE_TYPES = [
    "image/jpeg",
    "image/png",
    "image/jpg",
    "application/pdf"
]

MAX_FILE_PATH_LENGTH = 500


class Upload(Base):
    __tablename__ = "uploads"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(
        Integer,
        ForeignKey("applications.id"),
        nullable=False,
        index=True
    )
    requirement_id = Column(
        Integer,
        ForeignKey("requirements.id"),
        nullable=True,
        index=True
    )
    file_path = Column(String(MAX_FILE_PATH_LENGTH), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size_kb = Column(Integer, nullable=True)
    uploaded_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    application = relationship("Application", back_populates="uploads")
    requirement = relationship("Requirement", back_populates="uploads")

    @validates("file_type")
    def validate_file_type(self, key, file_type):
        file_type = file_type.strip().lower()
        if file_type not in ALLOWED_FILE_TYPES:
            raise ValueError(
                f"Invalid file type: {file_type}. "
                f"Allowed types are: {ALLOWED_FILE_TYPES}"
            )
        return file_type

    @validates("file_path")
    def validate_file_path(self, key, file_path):
        file_path = file_path.strip()
        if not file_path:
            raise ValueError("File path cannot be empty")
        if len(file_path) > MAX_FILE_PATH_LENGTH:
            raise ValueError(
                f"File path too long. "
                f"Maximum length is {MAX_FILE_PATH_LENGTH} characters"
            )
        return file_path

    @validates("file_name")
    def validate_file_name(self, key, file_name):
        file_name = file_name.strip()
        if not file_name:
            raise ValueError("File name cannot be empty")
        return file_name

    @validates("file_size_kb")
    def validate_file_size(self, key, file_size_kb):
        if file_size_kb is not None and file_size_kb <= 0:
            raise ValueError("File size must be greater than zero")

        if file_size_kb is not None and file_size_kb > 5120:
            raise ValueError(
                "File too large. Maximum size is 5MB (5120KB)"
            )
        return file_size_kb

    def __repr__(self):
        return (
            f"<Upload id={self.id} "
            f"application_id={self.application_id} "
            f"file_name={self.file_name} "
            f"file_type={self.file_type}>"
        )