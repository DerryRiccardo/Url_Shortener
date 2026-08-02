from fastapi import HTTPException
from sqlmodel import Session
from app.models import User, UserCreate, UserLogin
from app.repositories import auth_repository
import bcrypt
from app.utils.jwt import create_access_token
from app.utils.response import AppException

def register_new_user(session: Session, user_data: UserCreate):
    existing = auth_repository.get_user_by_email(session, user_data.email)
    if existing:
        raise AppException(
            status_code=409, 
            message="Email is already taken", 
            code="EMAIL_ALREADY_EXISTS"
        )
    
    salt = bcrypt.gensalt()
    hash_password = bcrypt.hashpw(user_data.password.encode('utf-8'), salt).decode('utf-8')
    db_user = User(name=user_data.name, email=user_data.email, hashed_password=hash_password)
    
    return auth_repository.create_user(session, db_user)

def login_user(session: Session, login_data: UserLogin):
    user = auth_repository.get_user_by_email(session, login_data.email)
    
    if not user:
        raise AppException(
            status_code=404, 
            message="Email not found", 
            code="USER_NOT_FOUND"
        )

    is_valid = bcrypt.checkpw(login_data.password.encode('utf-8'), user.hashed_password.encode('utf-8'))
    if not is_valid:
        raise AppException(
            status_code=401, 
            message="Incorrect email or password", 
            code="INVALID_CREDENTIALS"
        )

    token_payload = {
        "sub": str(user.id),
        "role": user.role.value
    }

    access_token = create_access_token(data=token_payload)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }