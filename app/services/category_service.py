from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis import redis_client
from app.repositories.category import CategoryRepository
from app.repositories.note import NoteRepository


class CategoryService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = CategoryRepository(session)

    async def create_category(self, name: str, user_id: int):
        category = await self.repo.create(name, user_id)
        redis_client.delete(f"user:{user_id}:categories")
        return category

    async def list_categories(self, user_id: int):
        key = f"user:{user_id}:categories"
        cached = redis_client.get(key)
        if cached:
            return cached

        categories = await self.repo.get_all_by_user(user_id)
        # Convert SQLAlchemy models to dicts for JSON serialization
        data = [
            {"id": c.id, "name": c.name, "user_id": c.user_id}
            for c in categories
        ]
        redis_client.set(key, data)
        return data

    async def get_category(self, category_id: int, user_id: int):
        key = f"user:{user_id}:category:{category_id}"
        cached = redis_client.get(key)
        if cached:
            return cached

        category = await self.repo.get_by_id(category_id, user_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        data = {"id": category.id, "name": category.name, "user_id": category.user_id}
        redis_client.set(key, data)
        return data

    async def update_category(self, category_id: int, user_id: int, name: str):
        category = await self.repo.update(category_id, user_id, name)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        redis_client.delete(f"user:{user_id}:categories", f"user:{user_id}:category:{category_id}")
        return category

    async def delete_category(self, category_id: int, user_id: int):
        if not await self.repo.delete(category_id, user_id):
            raise HTTPException(status_code=404, detail="Category not found")

        redis_client.delete(
            f"user:{user_id}:categories",
            f"user:{user_id}:category:{category_id}",
            f"user:{user_id}:category:{category_id}:notes"
        )
        return True


class NoteService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.cat_repo = CategoryRepository(session)
        self.note_repo = NoteRepository(session)

    async def _verify_category_ownership(self, category_id: int, user_id: int):
        if not await self.cat_repo.get_by_id(category_id, user_id):
            raise HTTPException(status_code=404, detail="Category not found")

    async def list_notes(self, category_id: int, user_id: int):
        await self._verify_category_ownership(category_id, user_id)

        key = f"user:{user_id}:category:{category_id}:notes"
        cached = redis_client.get(key)
        if cached:
            return cached

        notes = await self.note_repo.get_all_by_category(category_id, user_id)
        data = [
            {"id": n.id, "title": n.title, "content": n.content, "category_id": n.category_id, "user_id": n.user_id}
            for n in notes
        ]
        redis_client.set(key, data)
        return data

    async def create_note(
        self, title: str, content: str, category_id: int, user_id: int
    ):
        await self._verify_category_ownership(category_id, user_id)
        note = await self.note_repo.create(title, content, category_id, user_id)
        redis_client.delete(f"user:{user_id}:category:{category_id}:notes")
        return note

    async def get_note(self, note_id: int, category_id: int, user_id: int):
        await self._verify_category_ownership(category_id, user_id)

        key = f"user:{user_id}:note:{note_id}"
        cached = redis_client.get(key)
        if cached:
            # Still verify category_id match
            if cached.get("category_id") != category_id:
                raise HTTPException(status_code=404, detail="Note not found in this category")
            return cached

        note = await self.note_repo.get_by_id(note_id, user_id)
        if not note or note.category_id != category_id:
            raise HTTPException(
                status_code=404, detail="Note not found in this category"
            )

        data = {"id": note.id, "title": note.title, "content": note.content, "category_id": note.category_id, "user_id": note.user_id}
        redis_client.set(key, data)
        return data

    async def update_note(
        self, note_id: int, category_id: int, user_id: int, title: str, content: str
    ):
        await self._verify_category_ownership(category_id, user_id)
        note = await self.note_repo.update(note_id, user_id, title, content)
        if not note or note.category_id != category_id:
            raise HTTPException(
                status_code=404, detail="Note not found in this category"
            )

        redis_client.delete(f"user:{user_id}:note:{note_id}", f"user:{user_id}:category:{category_id}:notes")
        return note

    async def delete_note(self, note_id: int, category_id: int, user_id: int):
        await self._verify_category_ownership(category_id, user_id)
        if not await self.note_repo.delete(note_id, user_id):
            raise HTTPException(status_code=404, detail="Note not found")

        redis_client.delete(f"user:{user_id}:note:{note_id}", f"user:{user_id}:category:{category_id}:notes")
        return True
