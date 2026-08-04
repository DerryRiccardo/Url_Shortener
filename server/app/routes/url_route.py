from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.database import get_session
from app.models import UrlCreate, UrlUpdate, UrlPublic, User, AnalyticsResponse
from app.services import url_service, analytics_service
from app.utils.response import SuccessResponse, ErrorResponse
from app.utils.jwt import get_current_user
from app.utils.logger import app_logger
import uuid

router = APIRouter()

URL_RESPONSES = {
    400: {"model": ErrorResponse, "description": "Bad Request / Validation Error"},
    401: {"model": ErrorResponse, "description": "Unauthorized"},
    404: {"model": ErrorResponse, "description": "URL Not Found"},
    409: {"model": ErrorResponse, "description": "Alias already in use"},
    422: {"model": ErrorResponse, "description": "Validation Error"}
}

@router.post("", response_model=SuccessResponse[UrlPublic], status_code=201, responses=URL_RESPONSES)
def create_url(url_data: UrlCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    app_logger.info(f"User {current_user.id} attempting to create short URL")
    data = url_service.create_short_url(session, url_data, current_user.id)
    app_logger.success(f"Short URL created: {data['alias']}")
    return SuccessResponse(message="Short URL created successfully", data=data)

@router.get("", response_model=SuccessResponse[list[UrlPublic]], status_code=200, responses=URL_RESPONSES)
def get_urls(page: int = 1, limit: int = 10, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    result = url_service.get_urls(session, current_user.id, page, limit)
    return SuccessResponse(message="URLs retrieved successfully", data=result["data"], meta=result["meta"])

@router.get("/{url_id}", response_model=SuccessResponse[UrlPublic], status_code=200, responses=URL_RESPONSES)
def get_url(url_id: uuid.UUID, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    data = url_service.get_url_by_id(session, url_id, current_user.id)
    return SuccessResponse(message="URL retrieved successfully", data=data)

@router.patch("/{url_id}", response_model=SuccessResponse[UrlPublic], status_code=200, responses=URL_RESPONSES)
def update_url(url_id: uuid.UUID, url_data: UrlUpdate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    app_logger.info(f"User {current_user.id} attempting to update URL {url_id}")
    data = url_service.update_url(session, url_id, url_data, current_user.id)
    app_logger.info(f"URL updated successfully: {url_id}")
    return SuccessResponse(message="URL updated successfully", data=data)

@router.delete("/{url_id}", status_code=204, responses=URL_RESPONSES)
def delete_url(url_id: uuid.UUID, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    url_service.delete_url(session, url_id, current_user.id)
    app_logger.info(f"User {current_user.id} deleted URL {url_id}")
    return None

@router.get("/{url_id}/analytics", response_model=SuccessResponse[AnalyticsResponse], status_code=200, responses=URL_RESPONSES)
def get_url_analytics(url_id: uuid.UUID, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    data = analytics_service.get_analytics(session, url_id, current_user.id)
    return SuccessResponse(message="Analytics retrieved successfully", data=data)
