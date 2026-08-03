import uuid
import os
import qrcode
from io import BytesIO
from sqlmodel import Session
from app.models import QrCode, QrCodeCreate, QrCodeUpdate
from app.repositories import qr_repository, url_repository
from app.utils.storage import upload_image_to_r2
from app.utils.response import AppException
from datetime import datetime

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")

def format_qr_public(qr: QrCode):
    return {
        "id": qr.id,
        "title": qr.title,
        "target_url": qr.target_url,
        "short_url_id": qr.short_url_id,
        "qr_color": qr.qr_color,
        "is_active": qr.is_active,
        "qr_image": qr.qr_image,
        "created_at": qr.created_at,
        "updated_at": qr.updated_at
    }

def create_qr_code(session: Session, qr_data: QrCodeCreate, owner_id: uuid.UUID):
    if not qr_data.url_id and not qr_data.long_url:
        raise AppException(status_code=400, message="Either url_id or long_url must be provided", code="VALIDATION_ERROR")
        
    target_url = qr_data.long_url
    
    # If url_id is provided, validate ownership and extract target
    if qr_data.url_id:
        url = url_repository.get_url_by_id(session, qr_data.url_id)
        if not url or url.owner_id != owner_id:
            raise AppException(status_code=404, message="Short URL not found", code="URL_NOT_FOUND")
            
        target_url = f"{BASE_URL}/{url.alias}"
        
        # Check if 1:1 relationship is violated (QR code already exists for this URL)
        existing_qr = session.query(QrCode).filter(QrCode.short_url_id == qr_data.url_id, QrCode.deleted_at == None).first()
        if existing_qr:
            raise AppException(status_code=409, message="QR Code already exists for this URL", code="QR_ALREADY_EXISTS")

    # Generate QR Code Image
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(target_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color=qr_data.qr_color, back_color="white")
    
    # Save image to BytesIO (file sementara di memori)
    img_byte_arr = BytesIO()
    img.save(img_byte_arr)
    
    # Generate unique filename
    qr_id = uuid.uuid4()
    filename = f"{qr_id}.png"
    
    # Upload to Cloudflare R2
    public_image_url = upload_image_to_r2(img_byte_arr, filename)
    
    # Save to Database
    db_qr = QrCode(
        id=qr_id,
        target_url=target_url,
        title=qr_data.title,
        qr_color=qr_data.qr_color,
        qr_image=public_image_url,
        owner_id=owner_id,
        short_url_id=qr_data.url_id
    )
    
    saved_qr = qr_repository.create_qr(session, db_qr)
    return format_qr_public(saved_qr)

def get_qrs(session: Session, user_id: uuid.UUID, page: int = 1, limit: int = 10):
    skip = (page - 1) * limit
    qrs = qr_repository.get_qrs_by_user(session, user_id, skip=skip, limit=limit)
    total = qr_repository.count_qrs_by_user(session, user_id)
    
    formatted_qrs = [format_qr_public(q) for q in qrs]
    
    return {
        "data": formatted_qrs,
        "meta": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit
        }
    }

def get_qr_by_id(session: Session, qr_id: uuid.UUID, user_id: uuid.UUID):
    qr = qr_repository.get_qr_by_id(session, qr_id)
    if not qr or qr.owner_id != user_id or qr.deleted_at is not None:
        raise AppException(status_code=404, message="QR Code not found", code="QR_NOT_FOUND")
    return format_qr_public(qr)

def delete_qr(session: Session, qr_id: uuid.UUID, user_id: uuid.UUID):
    qr = qr_repository.get_qr_by_id(session, qr_id)
    if not qr or qr.owner_id != user_id or qr.deleted_at is not None:
        raise AppException(status_code=404, message="QR Code not found", code="QR_NOT_FOUND")
        
    qr.deleted_at = datetime.now()
    qr.is_active = False
    qr_repository.update_qr(session, qr)
    return True

def update_qr(session: Session, qr_id: uuid.UUID, update_data: QrCodeUpdate, user_id: uuid.UUID):
    qr = qr_repository.get_qr_by_id(session, qr_id)
    if not qr or qr.owner_id != user_id or qr.deleted_at is not None:
        raise AppException(status_code=404, message="QR Code not found", code="QR_NOT_FOUND")
        
    # Update title
    if update_data.title is not None:
        qr.title = update_data.title
        
    # Jika warna diubah, kita HARUS membuat ulang gambarnya dari awal
    if update_data.qr_color is not None and update_data.qr_color != qr.qr_color:
        # 1. Regenerasi QR dengan warna baru
        qr_img = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr_img.add_data(qr.target_url)
        qr_img.make(fit=True)

        img = qr_img.make_image(fill_color=update_data.qr_color, back_color="white")
        
        img_byte_arr = BytesIO()
        img.save(img_byte_arr)
        
        # 2. Upload ulang ke Cloudflare dengan nama file baru agar cache terganti
        new_filename = f"{uuid.uuid4()}.png"
        public_image_url = upload_image_to_r2(img_byte_arr, new_filename)
        
        # 3. Update database
        qr.qr_color = update_data.qr_color
        qr.qr_image = public_image_url
        
    qr.updated_at = datetime.now()
    updated_qr = qr_repository.update_qr(session, qr)
    
    return format_qr_public(updated_qr)
