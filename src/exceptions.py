import uvicorn
from fastapi import APIRouter, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.model.model_exception import (
    DatabaseConnectionError,
    DuplicateEntryError,
    InvalidQueryError,
    NotFoundError,
)


def init_global_exception_handlers(app: FastAPI):
    # Define global exception handler for HTTPExceptions
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.detail, "type": "HTTPException"},
        )

    # Define global exception handler for RequestValidationError
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        return JSONResponse(
            status_code=422,
            content={
                "message": "Validation Error",
                "details": exc.errors(),
                "type": "RequestValidationError",
            },
        )

    # Define global exception handler for NotFoundError
    @app.exception_handler(NotFoundError)
    async def not_found_exception_handler(request: Request, exc: NotFoundError):
        return JSONResponse(
            status_code=404,
            content={"message": exc.detail, "type": "NotFoundError"},
        )

    # Define global exception handler for DatabaseConnectionError
    @app.exception_handler(DatabaseConnectionError)
    async def database_connection_exception_handler(
        request: Request, exc: DatabaseConnectionError
    ):
        return JSONResponse(
            status_code=500,
            content={"message": exc.detail, "type": "DatabaseConnectionError"},
        )

    # Define global exception handler for DuplicateEntryError
    @app.exception_handler(DuplicateEntryError)
    async def duplicate_entry_exception_handler(
        request: Request, exc: DuplicateEntryError
    ):
        return JSONResponse(
            status_code=409,
            content={"message": exc.detail, "type": "DuplicateEntryError"},
        )

    # Define global exception handler for InvalidQueryError
    @app.exception_handler(InvalidQueryError)
    async def invalid_query_exception_handler(request: Request, exc: InvalidQueryError):
        return JSONResponse(
            status_code=400,
            content={"message": exc.detail, "type": "InvalidQueryError"},
        )

    # Define global exception handler for unhandled exceptions
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"message": str(exc), "type": "UnhandledException"},
        )
