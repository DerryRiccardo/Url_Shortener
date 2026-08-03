from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.database import get_session
from app.models import QrCodeCreate, QrCodePublic, QrCodeUpdate, User
from app.services import qr_service
from app.utils.response import SuccessResponse, ErrorResponse
from app.utils.jwt import get_current_user
from app.utils.logger import app_logger
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
    app_logger.info(f"User {current_user.id} attempting to create QR code")
    data = qr_service.create_qr_code(session, qr_data, current_user.id)
    app_logger.success(f"QR Code created: {data['id']}")
    return SuccessResponse(message="QR Code created successfully", data=data)

@router.get("", response_model=SuccessResponse[list[QrCodePublic]], status_code=200, responses=QR_RESPONSES)
def get_qr_codes(page: int = 1, limit: int = 10, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    result = qr_service.get_qrs(session, current_user.id, page, limit)
    return SuccessResponse(message="QR Codes retrieved successfully", data=result["data"], meta=result["meta"])

@router.get("/{qr_id}", response_model=SuccessResponse[QrCodePublic], status_code=200, responses=QR_RESPONSES)
def get_qr_code(qr_id: uuid.UUID, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    data = qr_service.get_qr_by_id(session, qr_id, current_user.id)
    return SuccessResponse(message="QR Code retrieved successfully", data=data)

@router.delete("/{qr_id}", status_code=204, responses=QR_RESPONSES)
def delete_qr_code(qr_id: uuid.UUID, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    qr_service.delete_qr(session, qr_id, current_user.id)
    app_logger.info(f"User {current_user.id} deleted QR Code {qr_id}")
    return None

@router.patch("/{qr_id}", response_model=SuccessResponse[QrCodePublic], status_code=200, responses=QR_RESPONSES)
def update_qr_code(qr_id: uuid.UUID, qr_data: QrCodeUpdate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    app_logger.info(f"User {current_user.id} attempting to update QR Code {qr_id}")
    data = qr_service.update_qr(session, qr_id, qr_data, current_user.id)
    app_logger.info(f"QR Code updated successfully: {qr_id}")
    return SuccessResponse(message="QR Code updated successfully", data=data)
