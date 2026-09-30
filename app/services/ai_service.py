import json
import logging
from fastapi import HTTPException
from groq import Groq
from app.config import settings


class AIService:
    """Сервис Groq; модель задаётся переменной GROQ_MODEL."""

    def __init__(self):
        self._client = None

    @property
    def client(self):
        if not settings.GROQ_API_KEY:
            raise RuntimeError("AI не настроен: добавьте GROQ_API_KEY")
        if self._client is None:
            self._client = Groq(api_key=settings.GROQ_API_KEY, timeout=30, max_retries=1)
        return self._client

    def _clean_json(self, text: str) -> str:
        """Убирает ```json обёртку если модель её добавила."""
        text = text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[-1]
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
        return text.strip()

    def complete(self, messages: list[dict], *, json_mode: bool = False) -> str:
        """Возвращает ответ AI или безопасную HTTP-ошибку для клиента."""
        try:
            options = {"model": settings.GROQ_MODEL, "messages": messages,
                       "temperature": 0.7, "max_tokens": 4096}
            if json_mode:
                options["response_format"] = {"type": "json_object"}
            response = self.client.chat.completions.create(**options)
            content = response.choices[0].message.content
            if not content:
                raise HTTPException(status_code=503, detail="AI вернул пустой ответ. Попробуйте ещё раз.")
            return content
        except HTTPException:
            raise
        except Exception as error:
            status = getattr(error, "status_code", None)
            body = getattr(error, "body", {})
            detail = body.get("error", body) if isinstance(body, dict) else {}
            code = detail.get("code") if isinstance(detail, dict) else None
            logging.getLogger(__name__).error(
                "Groq request failed: model=%s status=%s code=%s type=%s",
                settings.GROQ_MODEL, status, code, type(error).__name__,
            )
            if status == 404 or code == "model_not_found":
                message = "Модель AI недоступна. Администратору нужно проверить GROQ_MODEL и доступ к модели в Groq."
            elif status in (401, 403):
                message = "AI недоступен: администратору нужно проверить ключ и разрешения Groq."
            elif status == 429:
                raise HTTPException(status_code=429, detail="Превышен лимит запросов AI. Попробуйте позже.") from error
            elif not settings.GROQ_API_KEY:
                message = "AI не настроен: администратору нужно добавить GROQ_API_KEY."
            else:
                message = "Сервис AI временно недоступен. Попробуйте позже."
            raise HTTPException(status_code=503, detail=message) from error

    def _send_request(self, system_prompt: str, user_message: str) -> str:
        return self.complete([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ], json_mode=True)

    def generate_task(self, topic: str, difficulty: str, language: str) -> dict:
        """Генерирует задание по программированию."""

        system_prompt = """Ты — преподаватель программирования.
Генерируй задания строго в формате JSON.
Не добавляй ничего лишнего — только чистый JSON без пояснений."""

        user_message = f"""Создай задание по теме "{topic}"
для уровня "{difficulty}" на языке {language}.

Верни JSON строго в таком формате:
{{
    "title": "Название задания",
    "description": "Подробное описание задания на русском",
    "hints": ["подсказка 1", "подсказка 2", "подсказка 3"],
    "expected_output": "Что должна вывести программа"
}}"""

        raw = self._send_request(system_prompt, user_message)
        try:
            return json.loads(self._clean_json(raw))
        except (ValueError, TypeError) as error:
            raise HTTPException(status_code=503, detail="AI вернул некорректный ответ. Попробуйте ещё раз.") from error

    def check_code(self, task: str, code: str) -> dict:
        """Проверяет код студента и даёт обратную связь."""

        system_prompt = """Ты — строгий но добрый преподаватель Python.
Проверяй код объективно. Отвечай строго в формате JSON без лишнего текста."""

        user_message = f"""Задание: {task}

Код студента:
```python
{code}
```

Оцени и верни JSON:
{{
    "is_correct": true или false,
    "score": число от 0 до 100,
    "feedback": "Подробная обратная связь на русском",
    "suggestions": ["совет 1", "совет 2"]
}}"""

        raw = self._send_request(system_prompt, user_message)
        try:
            return json.loads(self._clean_json(raw))
        except (ValueError, TypeError) as error:
            raise HTTPException(status_code=503, detail="AI вернул некорректный ответ. Попробуйте ещё раз.") from error

    def explain_error(self, code: str, error: str, level: str) -> dict:
        """Объясняет ошибку простым языком под уровень студента."""

        level_map = {
            "beginner":     "новичку, который только начал учиться",
            "intermediate": "студенту со средним уровнем",
            "advanced":     "продвинутому студенту"
        }
        level_desc = level_map.get(level, "студенту")

        system_prompt = f"""Ты — терпеливый преподаватель Python.
Объясняй ошибки простым языком {level_desc}.
Отвечай строго в формате JSON без лишнего текста."""

        user_message = f"""Код:
```python
{code}
```

Ошибка: {error}

Верни JSON:
{{
    "error_type": "тип ошибки (например SyntaxError)",
    "explanation": "простое объяснение ошибки на русском",
    "fix_suggestion": "как конкретно исправить",
    "example": "пример исправленного кода"
}}"""

        raw = self._send_request(system_prompt, user_message)
        try:
            return json.loads(self._clean_json(raw))
        except (ValueError, TypeError) as error:
            raise HTTPException(status_code=503, detail="AI вернул некорректный ответ. Попробуйте ещё раз.") from error


# Единственный экземпляр
ai_service = AIService()