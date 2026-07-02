from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Service(Base):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    fee: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    requirements: Mapped[list["Requirement"]] = relationship(back_populates="service", cascade="all, delete-orphan")
    steps: Mapped[list["Step"]] = relationship(back_populates="service", cascade="all, delete-orphan")
    applications: Mapped[list["Application"]] = relationship(back_populates="service")


class Requirement(Base):
    __tablename__ = "requirements"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    mandatory: Mapped[bool] = mapped_column(Boolean, default=True)
    needs_upload: Mapped[bool] = mapped_column(Boolean, default=False)
    order_index: Mapped[int] = mapped_column(default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    service: Mapped["Service"] = relationship(back_populates="requirements")
    application_data: Mapped[list["ApplicationData"]] = relationship(back_populates="requirement")
    uploads: Mapped[list["UploadedDocument"]] = relationship(back_populates="requirement")


class Step(Base):
    __tablename__ = "steps"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id", ondelete="CASCADE"), index=True)
    order_index: Mapped[int] = mapped_column(default=0)
    description: Mapped[str] = mapped_column(Text)

    service: Mapped["Service"] = relationship(back_populates="steps")
