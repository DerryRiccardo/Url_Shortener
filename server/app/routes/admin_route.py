from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from app.database import get_session
from app.models import User, AdminSummaryResponse, UserPublic, UrlPublic, QrCodePublic
from app.services import admin_service
from app.utils.response import SuccessResponse, ErrorResponse
from app.utils.jwt import get_current_user, require_admin
from app.utils.logger import app_logger
import uuid
from typing import Any

router = APIRouter()

ADMIN_RESPONSES = {
    400: {"model": ErrorResponse, "description": "Bad Request / Validation Error"},
    401: {"model": ErrorResponse, "description": "Unauthorized"},
    403: {"model": ErrorResponse, "description": "Forbidden - Admin access required"},
    404: {"model": ErrorResponse, "description": "Resource Not Found"},
    422: {"model": ErrorResponse, "description": "Validation Error"}
}

# --- Admin routes ---
@router.get("/summary", response_model=SuccessResponse[AdminSummaryResponse], status_code=200, responses=ADMIN_RESPONSES)
def get_summary(session: Session = Depends(get_session), admin_user: User = Depends(require_admin)):
    data = admin_service.get_summary(session)
    return SuccessResponse(message="Admin summary retrieved", data=data)

@router.get("/users", response_model=SuccessResponse[Any], status_code=200, responses=ADMIN_RESPONSES)
def get_all_users(page: int = 1, limit: int = 10, session: Session = Depends(get_session), admin_user: User = Depends(require_admin)):
    result = admin_service.get_users(session, page, limit)
    return SuccessResponse(message="Users retrieved", data=result["data"], meta=result["meta"])

@router.patch("/users/{user_id}/status", response_model=SuccessResponse[UserPublic], status_code=200, responses=ADMIN_RESPONSES)
def update_user_status(user_id: uuid.UUID, is_active: bool = Query(...), session: Session = Depends(get_session), admin_user: User = Depends(require_admin)):
    app_logger.warning(f"Admin {admin_user.id} updating user {user_id} status to {is_active}")
    user = admin_service.update_user_status(session, user_id, is_active)
    return SuccessResponse(message="User status updated", data=user)

@router.get("/urls", response_model=SuccessResponse[Any], status_code=200, responses=ADMIN_RESPONSES)
def get_all_urls(page: int = 1, limit: int = 10, session: Session = Depends(get_session), admin_user: User = Depends(require_admin)):
    result = admin_service.get_urls(session, page, limit)
    return SuccessResponse(message="URLs retrieved", data=result["data"], meta=result["meta"])

@router.delete("/urls/{url_id}", status_code=204, responses=ADMIN_RESPONSES)
def delete_url_by_admin(url_id: uuid.UUID, session: Session = Depends(get_session), admin_user: User = Depends(require_admin)):
    app_logger.warning(f"Admin {admin_user.id} deleting URL {url_id}")
    admin_service.delete_url_as_admin(session, url_id)
    return None

@router.get("/qr-codes", response_model=SuccessResponse[Any], status_code=200, responses=ADMIN_RESPONSES)
def get_all_qr_codes(page: int = 1, limit: int = 10, session: Session = Depends(get_session), admin_user: User = Depends(require_admin)):
    result = admin_service.get_qr_codes(session, page, limit)
    return SuccessResponse(message="QR Codes retrieved", data=result["data"], meta=result["meta"])

@router.delete("/qr-codes/{qr_id}", status_code=204, responses=ADMIN_RESPONSES)
def delete_qr_by_admin(qr_id: uuid.UUID, session: Session = Depends(get_session), admin_user: User = Depends(require_admin)):
    admin_service.delete_qr_as_admin(session, qr_id)
    return None