import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.conversation import Conversation
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)

SESSION_TIMEOUT_MINUTES = 30


def create_conversation(
    user_id: int,
    db: Session
) -> tuple[Conversation, bool]:
    rns (conversation, created) 
    
    try:
        existing = get_active_conversation(
            user_id=user_id,
            db=db
        )

        if existing:
            now = datetime.now(timezone.utc)
            
            started_at = existing.started_at
            if started_at.tzinfo is None:
                started_at = started_at.replace(tzinfo=timezone.utc)
            
            time_since_start = now - started_at
            session_limit = timedelta(minutes=SESSION_TIMEOUT_MINUTES)

            if time_since_start <= session_limit:
                logger.info(
                    f"Resuming active conversation "
                    f"id={existing.id} for user_id={user_id}. "
                    f"Started {time_since_start} ago."
                )
                return existing, False
            else:
                existing.status = "abandoned"
                existing.ended_at = now
                db.commit()
                logger.info(
                    f"Abandoned stale conversation "
                    f"id={existing.id} for user_id={user_id}. "
                    f"Started {time_since_start} ago — past timeout."
                )

        conversation = Conversation(
            user_id=user_id,
            status="active"
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        logger.info(
            f"New conversation created id={conversation.id} "
            f"for user_id={user_id}"
        )
        return conversation, True

    except Exception as e:
        db.rollback()
        logger.error(f"Error creating conversation: {e}")
        raise


def get_conversation_by_id(
    conversation_id: int,
    db: Session
) -> Conversation | None:
   
    try:
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()

        if not conversation:
            logger.info(
                f"No conversation found with id={conversation_id}"
            )
        return conversation

    except Exception as e:
        logger.error(f"Error fetching conversation: {e}")
        raise


def get_conversations_by_user(
    user_id: int,
    db: Session
) -> list[Conversation]:
    """
    Fetch all conversations for a specific citizen.
    Returns most recent first.
    """
    try:
        conversations = db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).order_by(
            Conversation.started_at.desc()
        ).all()

        logger.info(
            f"Found {len(conversations)} conversations "
            f"for user_id={user_id}"
        )
        return conversations

    except Exception as e:
        logger.error(f"Error fetching conversations for user: {e}")
        raise


VALID_CONVERSATION_TRANSITIONS = {
    "active": ["completed", "abandoned"],
    "completed": [],
    "abandoned": []
}


def update_conversation_status(
    conversation_id: int,
    status: str,
    db: Session
) -> Conversation | None:
    
    try:
        conversation = get_conversation_by_id(
            conversation_id=conversation_id,
            db=db
        )

        if not conversation:
            logger.warning(
                f"Cannot update status — conversation "
                f"id={conversation_id} not found"
            )
            return None

        current_status = conversation.status
        allowed_next = VALID_CONVERSATION_TRANSITIONS.get(
            current_status, []
        )

        if status not in allowed_next:
            raise ValueError(
                f"Invalid status transition for "
                f"conversation id={conversation_id}. "
                f"Cannot move from '{current_status}' to '{status}'. "
                f"Allowed transitions from '{current_status}': "
                f"{allowed_next if allowed_next else 'none — terminal state'}"
            )

        conversation.status = status

        if status in ["completed", "abandoned"]:
            from datetime import datetime, timezone
            conversation.ended_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(conversation)
        logger.info(
            f"Conversation id={conversation_id} "
            f"transitioned from {current_status} to {status}"
        )
        return conversation

    except ValueError:
        raise

    except Exception as e:
        db.rollback()
        logger.error(f"Error updating conversation status: {e}")
        raise