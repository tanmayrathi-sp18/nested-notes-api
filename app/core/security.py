import hashlib
from datetime import UTC, datetime, timedelta

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _normalize_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def hash_password(password: str) -> str:
    return pwd_context.hash(_normalize_password(password))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(_normalize_password(plain_password), hashed_password)


def create_access_token(data: dict) -> str:
    now = datetime.now(UTC)
    expires_at = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = data.copy()
    to_encode.update(
        {
            "exp": expires_at,
            "iat": now,
        }
    )

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
