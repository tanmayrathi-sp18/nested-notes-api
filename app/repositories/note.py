from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.note import Note


class NoteRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self, title: str, content: str, category_id: int, user_id: int
    ) -> Note:
        note = Note(
            title=title, content=content, category_id=category_id, user_id=user_id
        )
        self.session.add(note)
        await self.session.commit()
        await self.session.refresh(note)
        return note

    async def get_all_by_category(
        self, category_id: int, user_id: int
    ) -> Sequence[Note]:
        result = await self.session.execute(
            select(Note).where(Note.category_id == category_id, Note.user_id == user_id)
        )
        return result.scalars().all()

    async def get_by_id(self, note_id: int, user_id: int) -> Note | None:
        result = await self.session.execute(
            select(Note).where(Note.id == note_id, Note.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def update(
        self, note_id: int, user_id: int, title: str, content: str
    ) -> Note | None:
        note = await self.get_by_id(note_id, user_id)
        if note:
            note.title = title
            note.content = content
            await self.session.commit()
            await self.session.refresh(note)
        return note

    async def delete(self, note_id: int, user_id: int) -> bool:
        note = await self.get_by_id(note_id, user_id)
        if note:
            await self.session.delete(note)
            await self.session.commit()
            return True
        return False
