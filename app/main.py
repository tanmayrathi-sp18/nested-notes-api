from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.auth import router as auth_router
from app.api.categories import router as category_router
from app.api.notes import router as note_router
from app.core.exceptions import (
    DomainError,
    EntityNotFoundError,
    PermissionDeniedError,
    ValidationError,
)

app = FastAPI(title="FastAPI Nested Notes")


@app.exception_handler(EntityNotFoundError)
async def entity_not_found_handler(request: Request, exc: EntityNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": exc.message},
    )


@app.exception_handler(PermissionDeniedError)
async def permission_denied_handler(request: Request, exc: PermissionDeniedError):
    return JSONResponse(
        status_code=403,
        content={"detail": exc.message},
    )


@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.message},
    )


@app.exception_handler(DomainError)
async def domain_exception_handler(request: Request, exc: DomainError):
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected domain error occurred"},
    )


app.include_router(auth_router)
app.include_router(category_router)
app.include_router(note_router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to the Nested Notes API. Visit /docs for interactive documentation."
    }
