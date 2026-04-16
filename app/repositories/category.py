from collections.abc import Sequence

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category


class CategoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, name: str, user_id: int) -> Category:
        category = Category(name=name, user_id=user_id)
        self.session.add(category)
        await self.session.commit()
        await self.session.refresh(category)
        return category

    async def get_all_by_user(self, user_id: int) -> Sequence[Category]:
        result = await self.session.execute(
            select(Category).where(Category.user_id == user_id)
        )
        return result.scalars().all()

    async def get_by_id(self, category_id: int, user_id: int) -> Category | None:
        result = await self.session.execute(
            select(Category).where(
                Category.id == category_id, Category.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def update(
        self, category_id: int, user_id: int, name: str
    ) -> Category | None:
        stmt = (
            update(Category)
            .where(Category.id == category_id, Category.user_id == user_id)
            .values(name=name)
            .returning(Category)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none()

    async def delete(self, category_id: int, user_id: int) -> bool:
        stmt = (
            delete(Category)
            .where(Category.id == category_id, Category.user_id == user_id)
            .returning(Category.id)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()

        return result.scalar_one_or_none() is not None
