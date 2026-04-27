from fastapi import FastAPI
from server.src.error_handling.base import AppException
from server.src.error_handling.handlers import (
    app_exception_handler,
    generic_exception_handler
)

def setup_error_handlers(app: FastAPI):

    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

