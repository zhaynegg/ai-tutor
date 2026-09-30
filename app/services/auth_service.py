from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional

from app.config import settings
from app.models.db_models import User
from app.models.schemas import UserRegister

# Контекст для хеширования паролей через bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    if len(password.encode("utf-8")) > 72:
        raise HTTPException(status_code=400, detail="Пароль должен быть не длиннее 72 байт")
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    if len(plain.encode("utf-8")) > 72:
        return False
    return pwd_context.verify(plain, hashed)


def create_token(username: str) -> str:
    """Создаёт JWT токен на 24 часа."""
    expire = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    data = {"sub": username, "exp": expire}
    return jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Optional[str]:
    """Декодирует токен, возвращает username или None."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload.get("sub")
    except JWTError:
        return None


def register_user(db: Session, data: UserRegister) -> User:
    """Регистрирует нового пользователя."""
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="Это имя пользователя занято")
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Этот email уже зарегистрирован")

    user = User(
        username=data.username,
        email=data.email,
        full_name=data.full_name,
        hashed_password=hash_password(data.password),
        is_verified=False,  # не подтверждён
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login_user(db: Session, username: str, password: str) -> str:
    """Проверяет данные и возвращает JWT токен."""
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")

    # Проверяем подтверждён ли email
    if not user.is_verified:
        raise HTTPException(
            status_code=403,
            detail=f"Email не подтверждён|{user.email}"
        )

    return create_token(user.username)


def get_current_user(db: Session, token: Optional[str]) -> Optional[User]:
    """Возвращает текущего пользователя по токену из cookie."""
    if not token:
        return None
    username = decode_token(token)
    if not username:
        return None
    return db.query(User).filter(User.username == username).first()