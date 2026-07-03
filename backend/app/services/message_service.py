import logging
from sqlalchemy.orm import Session
from app.models.message import Message

logger = logging.getLogger(__name__)


def create_message(
    conversation_id: int,
    role: str,
    content: str,
    input_type: str = "text",
    db: Session = None
) -> Message:
    """
    Save a new message to a conversation.
    Role must be: user, assistant, or system.
    Input type must be: text or voice.
    """
    try:
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            input_type=input_type
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        logger.info(
            f"Message created id={message.id} "
            f"conversation_id={conversation_id} "
            f"role={role}"
        )
        return message

    except Exception as e:
        db.rollback()
        logger.error(f"Error creating message: {e}")
        raise


def get_messages_by_conversation_id(
    conversation_id: int,
    db: Session,
    limit: int = 50
) -> list[Message]:
    """
    Fetch all messages in a conversation.
    Ordered oldest to newest so AI gets correct context.
    Limit defaults to 50 to prevent overloading the AI context window.
    """
    try:
        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(
            Message.created_at.asc()
        ).limit(limit).all()

        logger.info(
            f"Found {len(messages)} messages "
            f"for conversation_id={conversation_id}"
        )
        return messages

    except Exception as e:
        logger.error(f"Error fetching messages: {e}")
        raise


def get_last_message(
    conversation_id: int,
    db: Session
) -> Message | None:
    """
    Fetch the most recent message in a conversation.
    Useful for Davy to check what was last said
    before generating the next AI response.
    """
    try:
        message = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(
            Message.created_at.desc()
        ).first()

        return message

    except Exception as e:
        logger.error(f"Error fetching last message: {e}")
        raise


def get_messages_by_role(
    conversation_id: int,
    role: str,
    db: Session
) -> list[Message]:
    """
    Fetch all messages of a specific role in a conversation.
    Useful for filtering only citizen messages or only assistant messages.
    """
    try:
        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id,
            Message.role == role
        ).order_by(
            Message.created_at.asc()
        ).all()

        logger.info(
            f"Found {len(messages)} messages "
            f"with role={role} "
            f"for conversation_id={conversation_id}"
        )
        return messages

    except Exception as e:
        logger.error(f"Error fetching messages by role: {e}")
        raise


def count_messages(
    conversation_id: int,
    db: Session
) -> int:
    """
    Count total messages in a conversation.
    Useful for analytics and deciding when to summarise context.
    """
    try:
        count = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).count()

        return count

    except Exception as e:
        logger.error(f"Error counting messages: {e}")
        raise