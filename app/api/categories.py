from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryRead
from app.schemas.note import NoteCreate, NoteRead
from app.services.category_service import CategoryService, NoteService

router = APIRouter(prefix="/categories", tags=["categories and notes"])


@router.post("/", response_model=CategoryRead)
async def create_category(
    category_in: CategoryCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
):
    service = CategoryService(session)
    return await service.create_category(category_in.name, current_user.id)


@router.get("/", response_model=list[CategoryRead])
async def list_categories(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
):
    service = CategoryService(session)
    return await service.list_categories(current_user.id)


@router.get("/{category_id}", response_model=CategoryRead)
async def get_category(
    category_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
):
    service = CategoryService(session)
    return await service.get_category(category_id, current_user.id)


@router.put("/{category_id}", response_model=CategoryRead)
async def update_category(
    category_id: int,
    category_in: CategoryCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
):
    service = CategoryService(session)
    return await service.update_category(category_id, current_user.id, category_in.name)


@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
):
    service = CategoryService(session)
    if await service.delete_category(category_id, current_user.id):
        return {"detail": "Category deleted"}
    raise HTTPException(status_code=404, detail="Category not found")


# Keep only Collection-level nested endpoints here
@router.get("/{category_id}/notes", response_model=list[NoteRead])
async def list_notes(
    category_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
):
    service = NoteService(session)
    return await service.list_notes(category_id, current_user.id)


@router.post("/{category_id}/notes", response_model=NoteRead)
async def create_note(
    category_id: int,
    note_in: NoteCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
):
    service = NoteService(session)
    return await service.create_note(
        note_in.title, note_in.content, category_id, current_user.id
    )
