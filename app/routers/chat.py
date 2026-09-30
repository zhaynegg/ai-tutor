import traceback
from fastapi import APIRouter, HTTPException, Cookie, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from groq import Groq

from app.config import settings
from app.database import get_db
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/chat", tags=["AI Chat"])

# Клиент Groq
from app.services.ai_service import ai_service


class ChatMessage(BaseModel):
    message: str
    history: list[dict] = []  # история сообщений [{role, content}, ...]


@router.post("/send")
def send_message(
    data: ChatMessage,
    db: Session = Depends(get_db),
    access_token: Optional[str] = Cookie(default=None)
):
    """
    Принимает сообщение студента и историю чата.
    Возвращает ответ AI.
    История хранится на фронтенде и передаётся с каждым запросом.
    """
    if not get_current_user(db, access_token):
        raise HTTPException(status_code=401, detail="Необходима авторизация")
    try:
        # Системный промпт — AI знает свою роль
        system_prompt = """Ты — дружелюбный и терпеливый преподаватель программирования на Python.

Твои правила:
1. Объясняй просто и понятно, используй аналогии
2. Давай подсказки, но НЕ пиши готовый код если студент не просит
3. Если студент просит объяснить ошибку — объясни причину и как исправить
4. Отвечай на русском языке
5. Используй примеры кода когда это помогает пониманию
6. Будь поддерживающим — ошибаться это нормально
7. Если вопрос не про программирование — вежливо перенаправь"""

        # Собираем историю сообщений для контекста
        messages = [{"role": "system", "content": system_prompt}]

        # Добавляем историю (максимум 10 последних сообщений)
        for msg in data.history[-10:]:
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })

        # Добавляем новое сообщение студента
        messages.append({"role": "user", "content": data.message})

        # Отправляем в Groq
        response = ai_service.client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
        )

        ai_response = response.choices[0].message.content

        return {
            "response": ai_response,
            "status": "ok"
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))