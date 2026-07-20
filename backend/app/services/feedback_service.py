import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.feedback import Feedback

logger = logging.getLogger(__name__)


def create_feedback(
    message_id: int,
    rating: int,
    db: Session,
    comment: str = None
) -> Feedback:
   
    try:
        existing = get_feedback_by_message(
            message_id=message_id,
            db=db
        )

        if existing:
            raise ValueError(
                f"Feedback already exists for "
                f"message_id={message_id}. "
                f"A message can only be rated once."
            )

        feedback = Feedback(
            message_id=message_id,
            rating=rating,
            comment=comment
        )
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        logger.info(
            f"Feedback created id={feedback.id} "
            f"message_id={message_id} "
            f"rating={rating}"
        )
        return feedback

    except ValueError:
        raise

    except IntegrityError:
        db.rollback()
        raise ValueError(
            f"Feedback already exists for "
            f"message_id={message_id}."
        )

    except Exception as e:
        db.rollback()
        logger.error(f"Error creating feedback: {e}")
        raise


def get_feedback_by_message(
    message_id: int,
    db: Session
) -> Feedback | None:
    
    try:
        feedback = db.query(Feedback).filter(
            Feedback.message_id == message_id
        ).first()

        return feedback

    except Exception as e:
        logger.error(f"Error fetching feedback: {e}")
        raise


def get_feedback_by_id(
    feedback_id: int,
    db: Session
) -> Feedback | None:
   
    try:
        feedback = db.query(Feedback).filter(
            Feedback.id == feedback_id
        ).first()

        if not feedback:
            logger.info(
                f"No feedback found with id={feedback_id}"
            )
        return feedback

    except Exception as e:
        logger.error(f"Error fetching feedback by id: {e}")
        raise


def get_all_feedback(
    db: Session,
    limit: int = 100
) -> list[Feedback]:
   
    try:
        feedback_list = db.query(Feedback).order_by(
            Feedback.created_at.desc()
        ).limit(limit).all()

        logger.info(f"Fetched {len(feedback_list)} feedback records")
        return feedback_list

    except Exception as e:
        logger.error(f"Error fetching all feedback: {e}")
        raise


def get_low_rated_feedback(
    db: Session,
    threshold: int = 2
) -> list[Feedback]:
   
    try:
        low_rated = db.query(Feedback).filter(
            Feedback.rating <= threshold
        ).order_by(
            Feedback.created_at.desc()
        ).all()

        logger.info(
            f"Found {len(low_rated)} feedback records "
            f"with rating <= {threshold}"
        )
        return low_rated

    except Exception as e:
        logger.error(f"Error fetching low rated feedback: {e}")
        raise


def get_feedback_summary(db: Session) -> dict:
  
    try:
        all_feedback = db.query(Feedback).all()

        if not all_feedback:
            return {
                "total_feedback": 0,
                "average_rating": None,
                "distribution": {
                    "1": 0, "2": 0, "3": 0, "4": 0, "5": 0
                }
            }

        total = len(all_feedback)
        average = sum(f.rating for f in all_feedback) / total

        distribution = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}
        for f in all_feedback:
            distribution[str(f.rating)] += 1

        summary = {
            "total_feedback": total,
            "average_rating": round(average, 2),
            "distribution": distribution
        }

        logger.info(
            f"Feedback summary: {total} total, "
            f"average={round(average, 2)}"
        )
        return summary

    except Exception as e:
        logger.error(f"Error generating feedback summary: {e}")
        raise