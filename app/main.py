from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.categories import router as category_router
from app.api.notes import router as note_router

app = FastAPI(title="FastAPI Nested Notes")

app.include_router(auth_router)
app.include_router(category_router)
app.include_router(note_router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to the Nested Notes API. Visit /docs for interactive documentation."
    }
