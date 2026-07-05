from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.schemas import UserCreate, UserLookup, UserRead
from app.services.flow_manager import get_or_create_user_by_phone

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    user = get_or_create_user_by_phone(db, payload.phone_number, payload.preferred_language)
    return user


@router.post("/lookup", response_model=UserRead)
def lookup_user(payload: UserLookup, db: Session = Depends(get_db)):
    if payload.phone_number is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="phone_number is required")

    user = db.query(User).filter(User.phone_number == payload.phone_number).one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
