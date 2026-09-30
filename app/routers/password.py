from app.config import PROJECT_ROOT
import traceback
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.models.db_models import User, PasswordResetCode
from app.services.mail_service import generate_code, send_reset_email
from app.services.auth_service import hash_password

router = APIRouter(prefix="/forgot-password", tags=["Password Reset"])
templates = Jinja2Templates(directory=str(PROJECT_ROOT / "templates"))


class ForgotPasswordRequest(BaseModel):
    email: str


class VerifyCodeRequest(BaseModel):
    email: str
    code: str


class ResetPasswordRequest(BaseModel):
    email: str
    code: str
    new_password: str


@router.get("")
async def forgot_page(request: Request):
    """Страница запроса сброса пароля."""
    return templates.TemplateResponse(
        request=request,
        name="forgot_password.html",
        context={}
    )


@router.post("/send-code")
async def send_code(
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    """Отправляет код на email пользователя."""
    # Ищем пользователя по email
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="Пользователь с таким email не найден"
        )

    # Удаляем старые коды
    db.query(PasswordResetCode).filter(
        PasswordResetCode.user_id == user.id
    ).delete()
    db.commit()

    # Генерируем новый код
    code = generate_code(6)
    expires_at = datetime.utcnow() + timedelta(minutes=15)

    reset_code = PasswordResetCode(
        user_id=user.id,
        email=user.email,
        code=code,
        expires_at=expires_at
    )
    db.add(reset_code)
    db.commit()

    # Отправляем письмо
    sent = await send_reset_email(user.email, code, user.username)
    if not sent:
        raise HTTPException(
            status_code=500,
            detail="Ошибка отправки письма. Проверьте email."
        )

    return {"message": "Код отправлен на ваш email", "email": data.email}


@router.post("/verify-code")
def verify_code(
    data: VerifyCodeRequest,
    db: Session = Depends(get_db)
):
    """Проверяет правильность кода."""
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    reset = db.query(PasswordResetCode).filter(
        PasswordResetCode.user_id == user.id,
        PasswordResetCode.code == data.code,
        PasswordResetCode.is_used == False
    ).first()

    if not reset:
        raise HTTPException(status_code=400, detail="Неверный код")

    if reset.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Код истёк. Запросите новый.")

    return {"message": "Код верный", "valid": True}


@router.post("/reset")
def reset_password(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """Сбрасывает пароль после проверки кода."""
    if len(data.new_password) < 6:
        raise HTTPException(
            status_code=400,
            detail="Пароль должен быть минимум 6 символов"
        )

    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    reset = db.query(PasswordResetCode).filter(
        PasswordResetCode.user_id == user.id,
        PasswordResetCode.code == data.code,
        PasswordResetCode.is_used == False
    ).first()

    if not reset or reset.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Код недействителен")

    # Меняем пароль
    user.hashed_password = hash_password(data.new_password)

    # Помечаем код как использованный
    reset.is_used = True
    db.commit()

    return {"message": "Пароль успешно изменён!"}