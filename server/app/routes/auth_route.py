from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.database import get_session
from app.models import UserCreate, UserPublic, UserLogin, TokenResponse, User
from app.services import auth_service 
from app.utils.response import SuccessResponse, ErrorResponse
from app.utils.jwt import get_current_user
from app.utils.logger import app_logger

router = APIRouter()

@router.post("/register", response_model=SuccessResponse[UserPublic], status_code=201, responses={
    409: {"model": ErrorResponse, "description": "Email already exists"},
    422: {"model": ErrorResponse, "description": "Validation Error"}
    })
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    app_logger.info(f"Attempting to register new user: {user.email}")
    data = auth_service.register_new_user(session, user)
    app_logger.success(f"User registered successfully: {data.id}")
    return SuccessResponse(message="User registered successfully", data=data)

@router.post("/login", response_model=SuccessResponse[TokenResponse], status_code=200, responses={
    401: {"model": ErrorResponse, "description": "Incorrect email or password"},
    404: {"model": ErrorResponse, "description": "User not found"},
    422: {"model": ErrorResponse, "description": "Validation Error"}
})
def login(login_data: UserLogin, session: Session = Depends(get_session)):
    app_logger.info(f"User attempting login: {login_data.email}")
    data = auth_service.login_user(session, login_data)
    app_logger.success(f"Login successful for user: {login_data.email}")
    return SuccessResponse(message="Login successful", data=data)

@router.get("/me", response_model=SuccessResponse[UserPublic], status_code=200)
def get_me(current_user: User = Depends(get_current_user)):
    return SuccessResponse(message="Profile retrieved successfully", data=current_user)