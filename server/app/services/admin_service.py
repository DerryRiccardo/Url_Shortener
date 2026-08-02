import uuid
import os
from sqlmodel import Session
from app.repositories import admin_repository, auth_repository, url_repository, qr_repository
from app.utils.response import AppException
from app.models import Role
from datetime import datetime

def get_summary(session: Session):
    total_users = admin_repository.get_total_users(session)
    total_urls = admin_repository.get_total_urls(session)
    active_urls = admin_repository.get_total_active_urls(session)
    inactive_urls = total_urls - active_urls
    total_qr_codes = admin_repository.get_total_qr_codes(session)
    total_clicks = admin_repository.get_total_global_clicks(session)
    
    return {
        "total_users": total_users,
        "total_urls": total_urls,
        "active_urls": active_urls,
        "inactive_urls": inactive_urls,
        "total_qr_codes": total_qr_codes,
        "total_clicks": total_clicks
    }

def get_users(session: Session, page: int, limit: int):
    skip = (page - 1) * limit
    users, total = admin_repository.get_all_users(session, skip, limit)
    
    return {
        "data": users,
        "meta": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit
        }
    }

def update_user_status(session: Session, target_user_id: uuid.UUID, is_active: bool):
    user = auth_repository.get_user_by_id(session, target_user_id)
    if not user:
        raise AppException(status_code=404, message="User not found", code="USER_NOT_FOUND")
        
    user.is_active = is_active
    auth_repository.update_user(session, user)
    return user

def get_urls(session: Session, page: int, limit: int):
    skip = (page - 1) * limit
    urls, total = admin_repository.get_all_urls(session, skip, limit)
    
    return {
        "data": urls,
        "meta": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit
        }
    }

def get_qr_codes(session: Session, page: int, limit: int):
    skip = (page - 1) * limit
    qrs, total = admin_repository.get_all_qr_codes(session, skip, limit)
    
    return {
        "data": qrs,
        "meta": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit
        }
    }

def delete_url_as_admin(session: Session, target_url_id: uuid.UUID):
    url = url_repository.get_url_by_id(session, target_url_id)
    if not url:
        raise AppException(status_code=404, message="URL not found", code="URL_NOT_FOUND")
    
    url.deleted_at = datetime.now()
    url.is_active = False
    url_repository.update_url(session, url)
    return url

def delete_qr_as_admin(session: Session, target_qr_id: uuid.UUID):
    qr = qr_repository.get_qr_by_id(session, target_qr_id)
    if not qr:
        raise AppException(status_code=404, message="QR Code not found", code="QR_NOT_FOUND")
        
    qr.deleted_at = datetime.now()
    qr.is_active = False
    qr_repository.update_qr(session, qr)
    return qr
