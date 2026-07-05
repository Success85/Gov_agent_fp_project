from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship, validates
from app.db.base import Base


class Step(Base):
    __tablename__ = "steps"

    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False, index=True)
    step_no = Column(Integer, nullable=False)
    instruction = Column(Text, nullable=False)
    instruction_rw = Column(Text, nullable=False)

    # Relationships
    service = relationship("Service", back_populates="steps")

    @validates("step_no")
    def validate_step_no(self, key, step_no):
        if step_no < 1:
            raise ValueError("Step number must be 1 or greater")
        return step_no

    @validates("instruction")
    def validate_instruction(self, key, instruction):
        instruction = instruction.strip()
        if not instruction:
            raise ValueError("Step instruction cannot be empty")
        return instruction

    @validates("instruction_rw")
    def validate_instruction_rw(self, key, instruction_rw):
        instruction_rw = instruction_rw.strip()
        if not instruction_rw:
            raise ValueError(
                "Kinyarwanda step instruction cannot be empty"
            )
        return instruction_rw

    def __repr__(self):
        return (
            f"<Step id={self.id} "
            f"service_id={self.service_id} "
            f"step_no={self.step_no}>"
        )