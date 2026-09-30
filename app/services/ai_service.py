import json
import time
from groq import Groq
from app.config import settings


class AIService:
    """
    Сервис для работы с Groq API.
    Модель: llama-3.3-70b-versatile — бесплатная, быстрая, умная.
    Лимит: 14400 запросов в день, 30 запросов в минуту.
    """

    MODEL = "llama-3.3-70b-versatile"

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

    def _send_request(self, system_prompt: str, user_message: str) -> str:
        """Отправляет запрос в Groq и возвращает текст ответа."""
        try:
            response = self.client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=1024,
            )
            return response.choices[0].message.content

        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "rate_limit" in error_str.lower():
                raise Exception(
                    "Превышен лимит запросов Groq. "
                    "Подожди минуту и попробуй снова."
                )
            raise Exception(f"Ошибка Groq API: {error_str}")

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
        return json.loads(self._clean_json(raw))

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
        return json.loads(self._clean_json(raw))

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
        return json.loads(self._clean_json(raw))


# Единственный экземпляр
ai_service = AIService()