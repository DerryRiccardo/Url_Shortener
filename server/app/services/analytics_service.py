import hashlib
from fastapi import Request
from sqlmodel import Session
from app.models import ClickEvent
from app.repositories import analytics_repository, url_repository
from app.utils.response import AppException
from user_agents import parse
import uuid

def record_click(session: Session, url_id: uuid.UUID, request: Request):
    # Extracts data from the Request object and records a ClickEvent.
    user_agent_string = request.headers.get("user-agent", "")
    referrer = request.headers.get("referer", None)
    
    # Hash the IP address for privacy
    client_ip = request.client.host if request.client else "unknown"
    ip_hash = hashlib.sha256(client_ip.encode('utf-8')).hexdigest()
    
    # Parse User-Agent untuk browser, OS, dan device type
    ua = parse(user_agent_string)
    
    browser = ua.browser.family
    os = ua.os.family
    
    device_type = "Desktop"
    if ua.is_mobile:
        device_type = "Mobile"
    elif ua.is_tablet:
        device_type = "Tablet"
    elif ua.is_bot:
        device_type = "Bot"
        
    click_event = ClickEvent(
        url_id=url_id,
        ip_hash=ip_hash,
        user_agent=user_agent_string[:255] if user_agent_string else None,
        referrer=referrer[:255] if referrer else None,
        browser=browser,
        os=os,
        device_type=device_type
    )
    
    analytics_repository.create_click_event(session, click_event)

def get_analytics(session: Session, url_id: uuid.UUID, owner_id: uuid.UUID):
    url = url_repository.get_url_by_id(session, url_id)
    if not url or url.owner_id != owner_id or url.deleted_at is not None:
        raise AppException(status_code=404, message="URL not found", code="URL_NOT_FOUND")
        
    total_clicks = analytics_repository.get_total_clicks(session, url_id)
    unique_visitors = analytics_repository.get_unique_visitors(session, url_id)
    clicks_by_date = analytics_repository.get_clicks_by_date(session, url_id)
    top_referrers = analytics_repository.get_top_referrers(session, url_id)
    devices = analytics_repository.get_devices(session, url_id)
    browsers = analytics_repository.get_browsers(session, url_id)
    
    return {
        "url_id": url.id,
        "alias": url.alias,
        "total_clicks": total_clicks,
        "unique_visitors": unique_visitors,
        "clicks_by_date": clicks_by_date,
        "top_referrers": top_referrers,
        "devices": devices,
        "browsers": browsers
    }
