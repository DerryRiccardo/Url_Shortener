import os
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session
from app.database import get_session
from app.repositories import auth_repository
from app.utils.response import AppException
from app.models import User
import uuid

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES"))

def create_access_token(data: dict):
    to_encode = data.copy()
    
    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

# Authorize di Swagger UI
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), session: Session = Depends(get_session)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        token_id = payload.get("sub")
        if token_id is None:
            raise AppException(status_code=401, message="Invalid token", code="UNAUTHORIZED")

        user = auth_repository.get_user_by_id(session, uuid.UUID(token_id))
        if not user or not user.is_active:
            raise AppException(status_code=401, message="Invalid token", code="UNAUTHORIZED")
        
        return user
    except jwt.ExpiredSignatureError: # token expired
        raise AppException(status_code=401, message="Token expired", code="TOKEN_EXPIRED")
    except jwt.PyJWTError: # invalid token
        raise AppException(status_code=401, message="Could not validate credentials", code="UNAUTHORIZED")

def require_admin(current_user: User = Depends(get_current_user)):
    from app.models import Role
    if current_user.role != Role.admin:
        raise AppException(
            status_code=403,
            message="You don't have permission to perform this action",
            code="INSUFFICIENT_PERMISSIONS"
        )
    return current_user
