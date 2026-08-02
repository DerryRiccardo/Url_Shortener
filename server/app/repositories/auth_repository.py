from sqlmodel import Session, select
from app.models import User
from pydantic import EmailStr
import uuid

def get_user_by_email(session: Session, email: EmailStr):
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()

def create_user(session: Session, user: User):
    session.add(user)
    session.commit()
    session.refresh(user)
    return user 

def get_user_by_id(session: Session, user_id: uuid.UUID):
    return session.get(User, user_id)