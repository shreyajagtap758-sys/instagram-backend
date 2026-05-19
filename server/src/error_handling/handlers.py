# core/errors/handlers.py

from fastapi import Request
from fastapi.responses import JSONResponse
from server.src.error_handling.base import AppException


def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error,
            "message": exc.message,
            **exc.extra
        }
    )


def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_error",
            "message": "Something went wrong"
        }
    )