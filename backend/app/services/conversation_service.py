import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.conversation import Conversation

logger = logging.getLogger(__name__)


def create_conversation(
    user_id: int,
    db: Session
) -> Conversation:
    """
    Start a new conversation for a citizen.
    """
    try:
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
        return conversation

    except Exception as e:
        db.rollback()
        logger.error(f"Error creating conversation: {e}")
        raise


def get_conversation_by_id(
    conversation_id: int,
    db: Session
) -> Conversation | None:
    """
    Fetch a single conversation by its ID.
    Returns None if not found.
    """
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


def update_conversation_status(
    conversation_id: int,
    status: str,
    db: Session
) -> Conversation | None:
    """
    Update the status of a conversation.
    Valid statuses: active, completed, abandoned.
    """
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

        conversation.status = status

        if status in ["completed", "abandoned"]:
            from datetime import datetime, timezone
            conversation.ended_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(conversation)
        logger.info(
            f"Conversation id={conversation_id} "
            f"status updated to {status}"
        )
        return conversation

    except Exception as e:
        db.rollback()
        logger.error(f"Error updating conversation status: {e}")
        raise


def get_active_conversation(
    user_id: int,
    db: Session
) -> Conversation | None:
    """
    Fetch the current active conversation for a citizen.
    Returns None if no active conversation exists.
    """
    try:
        conversation = db.query(Conversation).filter(
            Conversation.user_id == user_id,
            Conversation.status == "active"
        ).order_by(
            Conversation.started_at.desc()
        ).first()

        return conversation

    except Exception as e:
        logger.error(f"Error fetching active conversation: {e}")
        raise