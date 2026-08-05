from fastapi import APIRouter, Depends, Request, BackgroundTasks
from fastapi.responses import RedirectResponse
from sqlmodel import Session
from app.database import get_session
from app.services import url_service, analytics_service
from app.utils.response import ErrorResponse

router = APIRouter()

@router.get("/{alias:path}", responses={
    404: {"model": ErrorResponse, "description": "URL Not Found or Inactive"},
    422: {"model": ErrorResponse, "description": "Validation Error"}
})
def redirect_to_url(alias: str, request: Request, background_tasks: BackgroundTasks, session: Session = Depends(get_session)):
    url = url_service.resolve_alias_for_redirect(session, alias)
    
    background_tasks.add_task(analytics_service.record_click, session, url.id, request)
    
    return RedirectResponse(url=url.long_url, status_code=302)
