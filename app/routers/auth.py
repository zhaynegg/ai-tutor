from fastapi import APIRouter, Depends, Response, Cookie, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta

from app.config import settings
from app.database import get_db
from app.models.schemas import UserRegister, UserLogin
from app.models.db_models import EmailVerification
from app.services.auth_service import register_user, login_user
from app.services.mail_service import generate_code, send_verification_email

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
async def register(data: UserRegister, db: Session = Depends(get_db)):
    """Регистрация — отправляет код подтверждения на email."""
    user = register_user(db, data)

    # Генерируем код подтверждения
    code = generate_code(6)
    expires_at = datetime.utcnow() + timedelta(minutes=15)

    verification = EmailVerification(
        user_id=user.id,
        code=code,
        expires_at=expires_at
    )
    db.add(verification)
    db.commit()

    # Отправляем письмо
    if not await send_verification_email(user.email, code, user.username):
        db.delete(verification)
        db.delete(user)
        db.commit()
        raise HTTPException(status_code=503, detail="Не удалось отправить письмо. Попробуйте регистрацию позже.")

    return {
        "message": "Регистрация прошла успешно! Проверьте email для подтверждения.",
        "username": user.username,
        "email": user.email
    }


@router.post("/verify-email")
def verify_email(
    username: str,
    code: str,
    db: Session = Depends(get_db)
):
    """Подтверждает email по коду."""
    from app.models.db_models import User
    user = db.query(User).filter(User.username == username).first()
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    verification = db.query(EmailVerification).filter(
        EmailVerification.user_id == user.id,
        EmailVerification.code == code,
        EmailVerification.is_used == False
    ).first()

    if not verification:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Неверный код")

    if verification.expires_at < datetime.utcnow():
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Код истёк")

    # Подтверждаем
    user.is_verified = True
    verification.is_used = True
    db.commit()

    return {"message": "Email подтверждён! Теперь вы можете войти."}


@router.post("/login")
def login(data: UserLogin, response: Response, db: Session = Depends(get_db)):
    """Вход."""
    token = login_user(db, data.username, data.password)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=settings.IS_RENDER,
        max_age=86400,
        samesite="lax"
    )
    return {"message": "Вход выполнен!", "username": data.username}


@router.post("/logout")
def logout(response: Response):
    """Выход."""
    response.delete_cookie("access_token")
    return {"message": "Выход выполнен"}