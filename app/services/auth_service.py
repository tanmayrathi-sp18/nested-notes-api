from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password, verify_password
from app.repositories.user import UserRepository
from app.schemas.user import Token, UserCreate, UserRead


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = UserRepository(session)

    async def register(self, user_in: UserCreate) -> UserRead:
        existing_user = await self.repo.get_by_email(user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        user = await self.repo.create(user_in.email, hash_password(user_in.password))
        return UserRead.model_validate(user)

    async def authenticate(self, email: str, password: str) -> Token:
        user = await self.repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return Token(
            access_token=create_access_token({"sub": str(user.id)}),
            token_type="bearer",  # noqa: S106
        )
