from sqlmodel import Session, select
from app.models import Url
import uuid

def create_url(session: Session, url: Url):
    session.add(url)
    session.commit()
    session.refresh(url)
    return url

def get_url_by_alias(session: Session, alias: str):
    statement = select(Url).where(Url.alias == alias)
    return session.exec(statement).first()

def get_url_by_id(session: Session, url_id: uuid.UUID):
    return session.get(Url, url_id)

def update_url(session: Session, url: Url):
    session.add(url)
    session.commit()
    session.refresh(url)
    return url

def get_urls_by_user(session: Session, owner_id: uuid.UUID, skip: int = 0, limit: int = 10):
    statement = select(Url).where(Url.owner_id == owner_id, Url.deleted_at == None).offset(skip).limit(limit)
    return session.exec(statement).all()

def count_urls_by_user(session: Session, owner_id: uuid.UUID):
    statement = select(Url).where(Url.owner_id == owner_id, Url.deleted_at == None)
    return len(session.exec(statement).all())
