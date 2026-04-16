from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.user import Token, UserCreate, UserRead
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserRead)
async def signup(
    user_in: UserCreate, session: Annotated[AsyncSession, Depends(get_db)]
):
    service = AuthService(session)
    return await service.register(user_in)


@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_db)],
):
    service = AuthService(session)
    return await service.authenticate(form_data.username, form_data.password)
