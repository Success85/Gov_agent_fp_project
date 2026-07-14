import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.user import User

logger = logging.getLogger(__name__)


def create_user(
    phone_number: str,
    preferred_language: str = "rw",
    db: Session = None
) -> User:
   
    try:
        user = User(
            phone_number=phone_number,
            preferred_language=preferred_language
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"New user created with id={user.id}")
        return user

    except IntegrityError:
        db.rollback()
        
        logger.warning(
            f"Registration attempt with already registered "
            f"phone number. user_id not created."
        )
        raise ValueError(
            "This phone number is already registered. "
            "Please log in instead."
        )

    except Exception as e:
        db.rollback()
        logger.error(f"Error creating user: {e}")
        raise


def get_user_by_phone(phone_number: str, db: Session) -> User | None:
    
    try:
        user = db.query(User).filter(
            User.phone_number == phone_number
        ).first()

        if not user:
            logger.info(f"No user found with phone={phone_number}")
        return user

    except Exception as e:
        logger.error(f"Error fetching user by phone: {e}")
        raise


def get_user_by_id(user_id: int, db: Session) -> User | None:
   
    try:
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            logger.info(f"No user found with id={user_id}")
        return user

    except Exception as e:
        logger.error(f"Error fetching user by id: {e}")
        raise


def get_or_create_user(
    phone_number: str,
    preferred_language: str = "rw",
    db: Session = None
) -> tuple[User, bool]:
    
    try:
        user = get_user_by_phone(phone_number=phone_number, db=db)
        if user:
            return user, False

        user = create_user(
            phone_number=phone_number,
            preferred_language=preferred_language,
            db=db
        )
        return user, True

    except Exception as e:
        logger.error(f"Error in get_or_create_user: {e}")
        raise