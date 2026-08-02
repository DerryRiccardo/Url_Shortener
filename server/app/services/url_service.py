import string
import secrets
import uuid
import os
from sqlmodel import Session
from datetime import datetime
from app.models import Url, UrlCreate, UrlUpdate
from app.repositories import url_repository
from app.utils.response import AppException

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")

def generate_random_alias(length=6):
    # membuat kolam karakter (52 huruf + 10 angka = 62 karakter)
    characters = string.ascii_letters + string.digits
    # menggabungkan karakter secara acak sebanyak panjang alias yang diinginkan
    return ''.join(secrets.choice(characters) for _ in range(length))

def format_url_public(url: Url):
    return {
        "id": url.id,
        "alias": url.alias,
        "short_url": f"{BASE_URL}/{url.alias}",
        "long_url": url.long_url,
        "title": url.title,
        "is_active": url.is_active,
        "expires_at": url.expires_at,
        "created_at": url.created_at,
        "updated_at": url.updated_at
    }

def create_short_url(session: Session, url_data: UrlCreate, owner_id: uuid.UUID):
    alias = ""
    if url_data.alias_mode.value == "custom":
        if not url_data.alias:
            raise AppException(status_code=400, message="Custom alias is required", code="VALIDATION_ERROR")
        alias = url_data.alias
        existing = url_repository.get_url_by_alias(session, alias)
        if existing:
            raise AppException(status_code=409, message="Alias is already in use", code="ALIAS_ALREADY_EXISTS")
    else:
        # random mode
        while True:
            alias = generate_random_alias()
            existing = url_repository.get_url_by_alias(session, alias)
            if not existing:
                break
                
    db_url = Url(
        alias=alias,
        long_url=url_data.long_url,
        title=url_data.title,
        alias_mode=url_data.alias_mode,
        expires_at=url_data.expires_at,
        owner_id=owner_id
    )
    
    saved_url = url_repository.create_url(session, db_url)
    return format_url_public(saved_url)

def get_url_by_id(session: Session, url_id: uuid.UUID, user_id: uuid.UUID):
    url = url_repository.get_url_by_id(session, url_id)
    if not url or url.owner_id != user_id:
        raise AppException(status_code=404, message="URL not found", code="URL_NOT_FOUND")
    return format_url_public(url)

def update_url(session: Session, url_id: uuid.UUID, url_data: UrlUpdate, user_id: uuid.UUID):
    url = url_repository.get_url_by_id(session, url_id)
    if not url or url.owner_id != user_id:
        raise AppException(status_code=404, message="URL not found", code="URL_NOT_FOUND")
        
    if url_data.alias and url_data.alias != url.alias:
        existing = url_repository.get_url_by_alias(session, url_data.alias)
        if existing:
             raise AppException(status_code=409, message="Alias is already in use", code="ALIAS_ALREADY_EXISTS")
        url.alias = url_data.alias
        
    if url_data.title is not None:
        url.title = url_data.title
        
    if url_data.expires_at is not None:
        url.expires_at = url_data.expires_at
        
    url.updated_at = datetime.now()
    saved_url = url_repository.update_url(session, url)
    return format_url_public(saved_url)

def get_urls(session: Session, user_id: uuid.UUID, page: int = 1, limit: int = 10):
    skip = (page - 1) * limit
    urls = url_repository.get_urls_by_user(session, user_id, skip=skip, limit=limit)
    total = url_repository.count_urls_by_user(session, user_id)
    
    formatted_urls = [format_url_public(u) for u in urls]
    
    return {
        "data": formatted_urls,
        "meta": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit
        }
    }

def delete_url(session: Session, url_id: uuid.UUID, user_id: uuid.UUID):
    url = url_repository.get_url_by_id(session, url_id)
    if not url or url.owner_id != user_id:
        raise AppException(status_code=404, message="URL not found", code="URL_NOT_FOUND")
        
    # Soft delete
    url.deleted_at = datetime.now()
    url.is_active = False
    url_repository.update_url(session, url)
    return None

def resolve_alias_for_redirect(session: Session, alias: str):
    url = url_repository.get_url_by_alias(session, alias)
    if not url:
        raise AppException(status_code=404, message="URL not found", code="URL_NOT_FOUND")
        
    if url.deleted_at or not url.is_active:
        raise AppException(status_code=404, message="URL is inactive or deleted", code="URL_INACTIVE")
        
    if url.expires_at and url.expires_at < datetime.now(url.expires_at.tzinfo):
        raise AppException(status_code=404, message="URL has expired", code="URL_EXPIRED")
        
    return url
