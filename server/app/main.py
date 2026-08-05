from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from app.database import create_db_and_tables
from app.routes import auth_route, url_route, redirect_route, qr_route, admin_route
from fastapi.responses import JSONResponse
from app.utils.response import AppException
from fastapi.exceptions import RequestValidationError
from app.utils.logger import app_logger, request_id_context_var
import uuid
import traceback

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Dijalankan sebelum server menerima request
    app_logger.info("Starting up server and initializing database...")
    create_db_and_tables()
    app_logger.info("Server is up and running!")
    yield 
    app_logger.info("Shutting down server...")

app = FastAPI(
    lifespan=lifespan,
    swagger_ui_parameters={"displayRequestDuration": True}
)

# Middleware untuk menambahkan Request ID ke setiap request
@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    # Generate random Request ID and bind it to context var
    req_id = uuid.uuid4().hex[:8]
    request_id_context_var.set(req_id)
    
    app_logger.debug(f"Incoming request: {request.method} {request.url.path}")
    response = await call_next(request) # Menjalankan endpoint request yang diminta user
    app_logger.debug(f"Outgoing response: {response.status_code}")
    
    return response

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    app_logger.error(f"Unhandled Exception: {str(exc)}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal Server Error",
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "details": None
            }
        }
    )

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    app_logger.warning(f"AppException {exc.status_code}: {exc.message} (Code: {exc.code})")
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
