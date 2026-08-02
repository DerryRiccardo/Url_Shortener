import uuid
from sqlmodel import Session, select, func
from app.models import ClickEvent
from sqlalchemy import Date

def create_click_event(session: Session, click: ClickEvent):
    session.add(click)
    session.commit()
    session.refresh(click)
    return click

def get_total_clicks(session: Session, url_id: uuid.UUID) -> int:
    statement = select(func.count(ClickEvent.id)).where(ClickEvent.url_id == url_id)
    return session.exec(statement).one()

def get_unique_visitors(session: Session, url_id: uuid.UUID) -> int:
    # menghitung jumlah pengunjung unik berdasarkan ip_hash
    statement = select(func.count(func.distinct(ClickEvent.ip_hash))).where(ClickEvent.url_id == url_id)
    return session.exec(statement).one()

def get_clicks_by_date(session: Session, url_id: uuid.UUID):
    statement = select(
        func.cast(ClickEvent.clicked_at, Date).label('date'), # mengubah tipe data datetime menjadi date
        func.count(ClickEvent.id).label('clicks')
    ).where(ClickEvent.url_id == url_id).group_by(func.cast(ClickEvent.clicked_at, Date)).order_by(func.cast(ClickEvent.clicked_at, Date))
    
    results = session.exec(statement).all()
    return [{"date": str(row.date), "clicks": row.clicks} for row in results]

# mengambil data dari mana asal orang yang klik link short url
def get_top_referrers(session: Session, url_id: uuid.UUID):
    statement = select(
        ClickEvent.referrer,
        func.count(ClickEvent.id).label('clicks')
    ).where(ClickEvent.url_id == url_id).group_by(ClickEvent.referrer).order_by(func.count(ClickEvent.id).desc()).limit(10) # top 10 teratas
    
    results = session.exec(statement).all()
    return [{"referrer": row.referrer if row.referrer else "Direct", "clicks": row.clicks} for row in results]

def get_devices(session: Session, url_id: uuid.UUID):
    statement = select(
        ClickEvent.device_type,
        func.count(ClickEvent.id).label('clicks')
    ).where(ClickEvent.url_id == url_id).group_by(ClickEvent.device_type).order_by(func.count(ClickEvent.id).desc())
    
    results = session.exec(statement).all()
    return [{"device_type": row.device_type if row.device_type else "Unknown", "clicks": row.clicks} for row in results]

def get_browsers(session: Session, url_id: uuid.UUID):
    statement = select(
        ClickEvent.browser,
        func.count(ClickEvent.id).label('clicks')
    ).where(ClickEvent.url_id == url_id).group_by(ClickEvent.browser).order_by(func.count(ClickEvent.id).desc())
    
    results = session.exec(statement).all()
    return [{"browser": row.browser if row.browser else "Unknown", "clicks": row.clicks} for row in results]
