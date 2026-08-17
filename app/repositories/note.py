from collections.abc import Sequence

from sqlalchemy import delete, func, select, update
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
        stmt = (
            update(Note)
            .where(Note.id == note_id, Note.user_id == user_id)
            .values(title=title, content=content)
            .returning(Note)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none()

    async def delete(self, note_id: int, user_id: int) -> bool:
        stmt = (
            delete(Note)
            .where(Note.id == note_id, Note.user_id == user_id)
            .returning(Note.id)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()

        return result.scalar_one_or_none() is not None

    async def get_stats_by_user(self, user_id: int) -> list[tuple[int, int]]:
        result = await self.session.execute(
            select(Note.category_id, func.count(Note.id))
            .where(Note.user_id == user_id)
            .group_by(Note.category_id)
        )
        return [(row[0], row[1]) for row in result.all()]
