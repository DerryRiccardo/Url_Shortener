from sqlmodel import Session, select
from app.models import QrCode
import uuid

def create_qr(session: Session, qr: QrCode):
    session.add(qr)
    session.commit()
    session.refresh(qr)
    return qr

def get_qr_by_id(session: Session, qr_id: uuid.UUID):
    return session.get(QrCode, qr_id)

def update_qr(session: Session, qr: QrCode):
    session.add(qr)
    session.commit()
    session.refresh(qr)
    return qr

def get_qrs_by_user(session: Session, owner_id: uuid.UUID, skip: int = 0, limit: int = 10):
    statement = select(QrCode).where(QrCode.owner_id == owner_id, QrCode.deleted_at == None).offset(skip).limit(limit)
    return session.exec(statement).all()

def count_qrs_by_user(session: Session, owner_id: uuid.UUID):
    statement = select(QrCode).where(QrCode.owner_id == owner_id, QrCode.deleted_at == None)
    return len(session.exec(statement).all())
