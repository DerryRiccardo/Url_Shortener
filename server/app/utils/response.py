from typing import Generic, TypeVar, Any, Optional
from pydantic import BaseModel
from fastapi import HTTPException

T = TypeVar("T") # tipe data generic bisa untuk apa aja

class SuccessResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str
    data: Optional[T] = None
    meta: Optional[dict] = None

class ErrorDetail(BaseModel):
    code: str
    details: Any = None
    
class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    error: ErrorDetail

class AppException(HTTPException):
    def __init__(self, status_code: int, message: str, code: str, details: Any = None):
        super().__init__(status_code=status_code, detail=message)
        self.message = message
        self.code = code
        self.details = details