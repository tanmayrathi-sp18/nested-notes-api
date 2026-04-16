from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.note import NoteCreate, NoteRead
from app.services.category_service import NoteService

router = APIRouter(prefix="/categories", tags=["categories and notes"])


@router.get("/{category_id}/notes/{note_id}", response_model=NoteRead)
async def get_note(
    category_id: int,
    note_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
):
    service = NoteService(session)
    return await service.get_note(note_id, category_id, current_user.id)


@router.put("/{category_id}/notes/{note_id}", response_model=NoteRead)
async def update_note(
    category_id: int,
    note_id: int,
    note_in: NoteCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
):
    service = NoteService(session)
    return await service.update_note(
        note_id, category_id, current_user.id, note_in.title, note_in.content
    )


@router.delete("/{category_id}/notes/{note_id}")
async def delete_note(
    category_id: int,
    note_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
):
    service = NoteService(session)
    if await service.delete_note(note_id, category_id, current_user.id):
        return {"detail": "Note deleted"}
    raise HTTPException(status_code=404, detail="Note not found")
