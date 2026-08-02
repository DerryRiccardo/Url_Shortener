import uuid
from sqlmodel import Session, select, func
from app.models import User, Url, QrCode, ClickEvent

def get_total_users(session: Session) -> int:
    return session.exec(select(func.count(User.id))).one()

def get_total_urls(session: Session) -> int:
    return session.exec(select(func.count(Url.id))).one()

def get_total_active_urls(session: Session) -> int:
    return session.exec(select(func.count(Url.id)).where(Url.is_active == True).where(Url.deleted_at == None)).one()

def get_total_qr_codes(session: Session) -> int:
    return session.exec(select(func.count(QrCode.id))).one()

def get_total_global_clicks(session: Session) -> int:
    return session.exec(select(func.count(ClickEvent.id))).one()

def get_all_users(session: Session, skip: int = 0, limit: int = 20):
    statement = select(User).offset(skip).limit(limit).order_by(User.created_at.desc())
    users = session.exec(statement).all()
    total = session.exec(select(func.count(User.id))).one()
    return users, total

def get_all_urls(session: Session, skip: int = 0, limit: int = 20):
    statement = select(Url).offset(skip).limit(limit).order_by(Url.created_at.desc())
    urls = session.exec(statement).all()
    total = session.exec(select(func.count(Url.id))).one()
    return urls, total

def get_all_qr_codes(session: Session, skip: int = 0, limit: int = 20):
    statement = select(QrCode).offset(skip).limit(limit).order_by(QrCode.created_at.desc())
    qrs = session.exec(statement).all()
    total = session.exec(select(func.count(QrCode.id))).one()
    return qrs, total
