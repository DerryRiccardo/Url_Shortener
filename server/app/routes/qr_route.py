from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.database import get_session
from app.models import QrCodeCreate, QrCodePublic, User
from app.services import qr_service
from app.utils.response import SuccessResponse, ErrorResponse
from app.utils.jwt import get_current_user
import uuid

router = APIRouter()

QR_RESPONSES = {
    400: {"model": ErrorResponse, "description": "Bad Request / Validation Error"},
    401: {"model": ErrorResponse, "description": "Unauthorized"},
    404: {"model": ErrorResponse, "description": "Not Found"},
    409: {"model": ErrorResponse, "description": "Conflict"},
    422: {"model": ErrorResponse, "description": "Validation Error"}
}

@router.post("", response_model=SuccessResponse[QrCodePublic], status_code=201, responses=QR_RESPONSES)
def create_qr_code(qr_data: QrCodeCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    data = qr_service.create_qr_code(session, qr_data, current_user.id)
    return SuccessResponse(message="QR Code created successfully", data=data)

@router.get("", response_model=SuccessResponse[list[QrCodePublic]], status_code=200, responses=QR_RESPONSES)
def get_qr_codes(page: int = 1, limit: int = 10, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    result = qr_service.get_qrs(session, current_user.id, page, limit)
    return SuccessResponse(message="QR Codes retrieved successfully", data=result["data"], meta=result["meta"])

@router.get("/{qr_id}", response_model=SuccessResponse[QrCodePublic], status_code=200, responses=QR_RESPONSES)
def get_qr_code(qr_id: uuid.UUID, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    data = qr_service.get_qr_by_id(session, qr_id, current_user.id)
    return SuccessResponse(message="QR Code retrieved successfully", data=data)
