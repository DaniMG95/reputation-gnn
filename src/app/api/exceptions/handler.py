import time
from fastapi import Request
from fastapi.responses import JSONResponse
from app.api.exceptions.custom_exceptions import AppBaseException
from core.observability.logger import Logger

logger = Logger(name="app.api.exceptions.handler")


async def app_exception_handler(request: Request, exc: AppBaseException):
    logger.error(f"APP ERROR: {exc.code} - {exc.message} at path {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "code": exc.code,
            "message": exc.message,
            "path": request.url.path,
            "timestamp": time.time()
        }
    )

async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"CRITICAL ERROR: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "critical_error",
            "message": "An unexpected error occurred. Please try again later.",
        }
    )