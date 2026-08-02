from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from app.database import create_db_and_tables
from app.routes import auth_route, url_route, redirect_route, qr_route, admin_route
from fastapi.responses import JSONResponse
from app.utils.response import AppException
from fastapi.exceptions import RequestValidationError

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Dijalankan sebelum server menerima request
    create_db_and_tables()
    yield 

app = FastAPI(lifespan=lifespan)

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.message,
            "error": {
                "code": exc.code,
                "details": exc.details
            }
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    details = []
    for error in exc.errors():
        # Mengambil nama field yang error (mengabaikan awalan 'body')
        field = ".".join([str(x) for x in error["loc"][1:]]) if len(error["loc"]) > 1 else str(error["loc"][0])
        details.append({
            "field": field,
            "message": error["msg"]
        })
        
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Validation error",
            "error": {
                "code": "VALIDATION_ERROR",
                "details": details
            }
        }
    )

app.include_router(auth_route.router, prefix="/api/auth", tags=["Auth"])
app.include_router(url_route.router, prefix="/api/urls", tags=["URLs"])
app.include_router(qr_route.router, prefix="/api/qr-codes", tags=["QR Codes"])
app.include_router(admin_route.router, prefix="/api/admin", tags=["Admin"])
app.include_router(redirect_route.router, prefix="", tags=["Redirect"])
