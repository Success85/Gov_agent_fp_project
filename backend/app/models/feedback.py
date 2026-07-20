from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship, validates
from datetime import datetime, timezone
from app.db.base import Base


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(
        Integer,
        ForeignKey("messages.id"),
        nullable=False,
        unique=True,
        index=True
    )
    rating = Column(Integer, nullable=False)
    comment = Column(String(500), nullable=True)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    # Database level constraint — rating must be 1 to 5
    __table_args__ = (
        CheckConstraint(
            "rating >= 1 AND rating <= 5",
            name="check_rating_range"
        ),
    )

    # Relationships
    message = relationship("Message", back_populates="feedback")

    @validates("rating")
    def validate_rating(self, key, rating):
        if not isinstance(rating, int):
            raise ValueError("Rating must be a whole number")
        if rating < 1 or rating > 5:
            raise ValueError(
                f"Invalid rating: {rating}. "
                "Rating must be between 1 and 5"
            )
        return rating

    @validates("comment")
    def validate_comment(self, key, comment):
        if comment is not None:
            comment = comment.strip()
            if len(comment) > 500:
                raise ValueError(
                    "Comment too long. "
                    "Maximum length is 500 characters"
                )
        return comment

    def __repr__(self):
        return (
            f"<Feedback id={self.id} "
            f"message_id={self.message_id} "
            f"rating={self.rating}>"
        )