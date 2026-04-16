from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import cache_result
from app.core.exceptions import EntityNotFoundError
from app.core.redis import redis_client
from app.repositories.category import CategoryRepository
from app.repositories.note import NoteRepository
from app.schemas.category import CategoryRead
from app.schemas.note import NoteRead


class CategoryService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = CategoryRepository(session)

    async def create_category(self, name: str, user_id: int):
        category = await self.repo.create(name, user_id)
        await redis_client.delete(f"user:{user_id}:categories")
        return category

    @cache_result(key_template="user:{user_id}:categories", schema=list[CategoryRead])
    async def list_categories(self, user_id: int):
        return await self.repo.get_all_by_user(user_id)

    @cache_result(
        key_template="user:{user_id}:category:{category_id}", schema=CategoryRead
    )
    async def get_category(self, category_id: int, user_id: int):
        category = await self.repo.get_by_id(category_id, user_id)
        if not category:
            raise EntityNotFoundError("Category not found")

        return category

    async def update_category(self, category_id: int, user_id: int, name: str):
        category = await self.repo.update(category_id, user_id, name)
        if not category:
            raise EntityNotFoundError("Category not found")

        await redis_client.delete(
            f"user:{user_id}:categories", f"user:{user_id}:category:{category_id}"
        )
        return category

    async def delete_category(self, category_id: int, user_id: int):
        if not await self.repo.delete(category_id, user_id):
            raise EntityNotFoundError("Category not found")

        await redis_client.delete(
            f"user:{user_id}:categories",
            f"user:{user_id}:category:{category_id}",
            f"user:{user_id}:category:{category_id}:notes",
        )
        return True


class NoteService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.cat_repo = CategoryRepository(session)
        self.note_repo = NoteRepository(session)

    async def _verify_category_ownership(self, category_id: int, user_id: int):
        if not await self.cat_repo.get_by_id(category_id, user_id):
            raise EntityNotFoundError("Category not found")

    @cache_result(
        key_template="user:{user_id}:category:{category_id}:notes",
        schema=list[NoteRead],
    )
    async def list_notes(self, category_id: int, user_id: int):
        await self._verify_category_ownership(category_id, user_id)
        return await self.note_repo.get_all_by_category(category_id, user_id)

    async def create_note(
        self, title: str, content: str, category_id: int, user_id: int
    ):
        await self._verify_category_ownership(category_id, user_id)
        note = await self.note_repo.create(title, content, category_id, user_id)
        await redis_client.delete(f"user:{user_id}:category:{category_id}:notes")
        return note

    @cache_result(key_template="user:{user_id}:note:{note_id}", schema=NoteRead)
    async def get_note(self, note_id: int, category_id: int, user_id: int):
        await self._verify_category_ownership(category_id, user_id)

        note = await self.note_repo.get_by_id(note_id, user_id)
        if not note or note.category_id != category_id:
            raise EntityNotFoundError("Note not found in this category")

        return note

    async def update_note(
        self, note_id: int, category_id: int, user_id: int, title: str, content: str
    ):
        await self._verify_category_ownership(category_id, user_id)
        note = await self.note_repo.update(note_id, user_id, title, content)
        if not note or note.category_id != category_id:
            raise EntityNotFoundError("Note not found in this category")

        await redis_client.delete(
            f"user:{user_id}:note:{note_id}",
            f"user:{user_id}:category:{category_id}:notes",
        )
        return note

    async def delete_note(self, note_id: int, category_id: int, user_id: int):
        await self._verify_category_ownership(category_id, user_id)
        if not await self.note_repo.delete(note_id, user_id):
            raise EntityNotFoundError("Note not found")

        await redis_client.delete(
            f"user:{user_id}:note:{note_id}",
            f"user:{user_id}:category:{category_id}:notes",
        )
        return True
