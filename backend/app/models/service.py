from sqlalchemy import Column, Integer, String, Text, Numeric
from sqlalchemy.orm import relationship, validates
from app.db.base import Base


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    name_rw = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    fee = Column(Numeric(10, 2), nullable=False, default=0.00)
    processing_days = Column(Integer, nullable=True)

    # Relationships
    requirements = relationship("Requirement", back_populates="service")
    steps = relationship("Step", back_populates="service")
    applications = relationship("Application", back_populates="service")

    @validates("name")
    def validate_name(self, key, name):
        name = name.strip()
        if not name:
            raise ValueError("Service name cannot be empty")
        return name

    @validates("name_rw")
    def validate_name_rw(self, key, name_rw):
        name_rw = name_rw.strip()
        if not name_rw:
            raise ValueError("Kinyarwanda service name cannot be empty")
        return name_rw

    @validates("fee")
    def validate_fee(self, key, fee):
        if fee < 0:
            raise ValueError("Service fee cannot be negative")
        return fee

    @validates("category")

    def validate_category(self, key, category):
        if not category:
           raise ValueError("Category cannot be empty")
    # Clean up capitalisation and whitespace
    category = category.strip().title()
    return category

    @validates("processing_days")
    def validate_processing_days(self, key, days):
        if days is not None and days < 0:
            raise ValueError("Processing days cannot be negative")
        return days

    def __repr__(self):
        return f"<Service id={self.id} name={self.name} category={self.category}>"
