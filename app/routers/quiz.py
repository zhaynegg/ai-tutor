from app.config import PROJECT_ROOT
import json
import traceback
from fastapi import APIRouter, Depends, Cookie, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.models.db_models import DiagnosticResult, User
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/quiz", tags=["Quiz"])
templates = Jinja2Templates(directory=str(PROJECT_ROOT / "templates"))

# ── ВОПРОСЫ ТЕСТА ─────────────────────────────────
# Структура: id, вопрос, тип (choice/code_read/practice),
# варианты ответов, правильный ответ, уровень сложности

QUESTIONS = [
    # ── BEGINNER ВОПРОСЫ ──
    {
        "id": 1,
        "level": "beginner",
        "type": "choice",
        "question": "Что выведет следующий код?\n\nprint(type(42))",
        "options": [
            "<class 'str'>",
            "<class 'int'>",
            "<class 'float'>",
            "42"
        ],
        "answer": 1  # индекс правильного ответа
    },
    {
        "id": 2,
        "level": "beginner",
        "type": "choice",
        "question": "Как правильно объявить список в Python?",
        "options": [
            "list = (1, 2, 3)",
            "list = {1, 2, 3}",
            "list = [1, 2, 3]",
            "list = <1, 2, 3>"
        ],
        "answer": 2
    },
    {
        "id": 3,
        "level": "beginner",
        "type": "code_read",
        "question": "Что выведет этот код?\n\nx = 10\nif x > 5:\n    print('A')\nelse:\n    print('B')",
        "options": ["A", "B", "10", "Ошибка"],
        "answer": 0
    },
    {
        "id": 4,
        "level": "beginner",
        "type": "choice",
        "question": "Какая функция используется для вывода текста в Python?",
        "options": ["echo()", "printf()", "print()", "console.log()"],
        "answer": 2
    },
    {
        "id": 5,
        "level": "beginner",
        "type": "code_read",
        "question": "Что выведет этот код?\n\nfor i in range(3):\n    print(i)",
        "options": ["1 2 3", "0 1 2", "0 1 2 3", "Ошибка"],
        "answer": 1
    },

    # ── INTERMEDIATE ВОПРОСЫ ──
    {
        "id": 6,
        "level": "intermediate",
        "type": "choice",
        "question": "Что такое lambda-функция в Python?",
        "options": [
            "Анонимная однострочная функция",
            "Функция без параметров",
            "Функция которая вызывает сама себя",
            "Встроенная функция Python"
        ],
        "answer": 0
    },
    {
        "id": 7,
        "level": "intermediate",
        "type": "code_read",
        "question": "Что выведет этот код?\n\ndef func(x, y=10):\n    return x + y\n\nprint(func(5))",
        "options": ["5", "10", "15", "Ошибка"],
        "answer": 2
    },
    {
        "id": 8,
        "level": "intermediate",
        "type": "choice",
        "question": "Что делает метод .get() у словаря?",
        "options": [
            "Удаляет элемент по ключу",
            "Возвращает значение по ключу или None если ключ не найден",
            "Добавляет новый элемент",
            "Возвращает все ключи словаря"
        ],
        "answer": 1
    },
    {
        "id": 9,
        "level": "intermediate",
        "type": "code_read",
        "question": "Что выведет этот код?\n\nnums = [1, 2, 3, 4, 5]\nresult = list(filter(lambda x: x % 2 == 0, nums))\nprint(result)",
        "options": [
            "[1, 3, 5]",
            "[2, 4]",
            "[1, 2, 3, 4, 5]",
            "Ошибка"
        ],
        "answer": 1
    },
    {
        "id": 10,
        "level": "intermediate",
        "type": "choice",
        "question": "Что такое декоратор в Python?",
        "options": [
            "Тип данных для хранения пар ключ-значение",
            "Функция которая модифицирует поведение другой функции",
            "Метод для форматирования строк",
            "Специальный цикл для перебора элементов"
        ],
        "answer": 1
    },

    # ── ADVANCED ВОПРОСЫ ──
    {
        "id": 11,
        "level": "advanced",
        "type": "code_read",
        "question": "Что выведет этот код?\n\nclass A:\n    x = 10\n\nclass B(A):\n    pass\n\nb = B()\nprint(b.x)",
        "options": ["None", "Ошибка", "10", "0"],
        "answer": 2
    },
    {
        "id": 12,
        "level": "advanced",
        "type": "choice",
        "question": "Что такое генератор (generator) в Python?",
        "options": [
            "Функция которая возвращает список",
            "Объект который генерирует значения по одному используя yield",
            "Встроенный метод для создания словарей",
            "Специальный тип цикла"
        ],
        "answer": 1
    },
    {
        "id": 13,
        "level": "advanced",
        "type": "code_read",
        "question": "Что выведет этот код?\n\ndef gen():\n    yield 1\n    yield 2\n    yield 3\n\ng = gen()\nprint(next(g))\nprint(next(g))",
        "options": ["1\n2", "1\n1", "[1, 2, 3]", "Ошибка"],
        "answer": 0
    },
    {
        "id": 14,
        "level": "advanced",
        "type": "choice",
        "question": "Что делает asyncio в Python?",
        "options": [
            "Ускоряет выполнение кода в несколько раз",
            "Позволяет писать асинхронный код для работы с I/O операциями",
            "Автоматически распараллеливает циклы",
            "Управляет памятью программы"
        ],
        "answer": 1
    },
    {
        "id": 15,
        "level": "advanced",
        "type": "code_read",
        "question": "Что выведет этот код?\n\ndata = {'a': 1, 'b': 2, 'c': 3}\nresult = {k: v*2 for k, v in data.items() if v > 1}\nprint(result)",
        "options": [
            "{'a': 2, 'b': 4, 'c': 6}",
            "{'b': 4, 'c': 6}",
            "{'b': 2, 'c': 3}",
            "Ошибка"
        ],
        "answer": 1
    }
]


def determine_level(answers: dict) -> tuple[str, float]:
    """
    Определяет уровень студента на основе ответов.
    Возвращает (уровень, процент правильных ответов).
    """
    beginner_correct = 0
    intermediate_correct = 0
    advanced_correct = 0

    beginner_total = 0
    intermediate_total = 0
    advanced_total = 0

    for q in QUESTIONS:
        qid = str(q["id"])
        correct = q["answer"]
        user_answer = answers.get(qid)

        if q["level"] == "beginner":
            beginner_total += 1
            if user_answer == correct:
                beginner_correct += 1
        elif q["level"] == "intermediate":
            intermediate_total += 1
            if user_answer == correct:
                intermediate_correct += 1
        elif q["level"] == "advanced":
            advanced_total += 1
            if user_answer == correct:
                advanced_correct += 1

    # Общий счёт
    total_correct = beginner_correct + intermediate_correct + advanced_correct
    total = len(QUESTIONS)
    score = round(total_correct / total * 100, 1)

    # Логика определения уровня
    beginner_pct = beginner_correct / beginner_total if beginner_total > 0 else 0
    inter_pct = intermediate_correct / intermediate_total if intermediate_total > 0 else 0
    adv_pct = advanced_correct / advanced_total if advanced_total > 0 else 0

    if adv_pct >= 0.6 and inter_pct >= 0.6:
        level = "advanced"
    elif inter_pct >= 0.5 and beginner_pct >= 0.6:
        level = "intermediate"
    else:
        level = "beginner"

    return level, score


def get_recommendations(level: str) -> dict:
    """Возвращает рекомендации курсов по уровню."""
    recommendations = {
        "beginner": {
            "title": "Начинающий (Beginner)",
            "description": "Отлично! Мы определили ваш начальный уровень. "
                          "Рекомендуем начать с основ Python.",
            "courses": [
                "Python с нуля",
                "Условия и циклы",
                "Функции",
                "Списки и словари"
            ],
            "tips": [
                "Решайте задания каждый день — даже по 30 минут",
                "Не бойтесь ошибок — это часть обучения",
                "Используйте AI-чат если что-то непонятно"
            ],
            "emoji": "🌱"
        },
        "intermediate": {
            "title": "Средний уровень (Intermediate)",
            "description": "Хорошие знания базового синтаксиса! "
                          "Время углубиться в более сложные концепции.",
            "courses": [
                "Функции и модули",
                "Работа со строками и списками",
                "Обработка ошибок (try/except)",
                "Основы ООП"
            ],
            "tips": [
                "Практикуйтесь на реальных проектах",
                "Изучайте стандартную библиотеку Python",
                "Читайте чужой код на GitHub"
            ],
            "emoji": "🚀"
        },
        "advanced": {
            "title": "Продвинутый уровень (Advanced)",
            "description": "Отличные знания Python! "
                          "Рекомендуем перейти к продвинутым темам.",
            "courses": [
                "Алгоритмы и структуры данных",
                "Работа с API",
                "Асинхронное программирование",
                "Оптимизация кода"
            ],
            "tips": [
                "Участвуйте в соревнованиях по программированию",
                "Создавайте собственные open-source проекты",
                "Изучайте архитектурные паттерны"
            ],
            "emoji": "⚡"
        }
    }
    return recommendations[level]


@router.get("")
async def quiz_page(
    request: Request,
    db: Session = Depends(get_db),
    access_token: Optional[str] = Cookie(default=None)
):
    """Страница диагностического теста."""
    user = get_current_user(db, access_token)
    if not user:
        return RedirectResponse(url="/login")

    # Если тест уже пройден — на результаты
    existing = db.query(DiagnosticResult).filter(
        DiagnosticResult.user_id == user.id
    ).first()
    if existing:
        return RedirectResponse(url="/quiz/result")

    return templates.TemplateResponse(
        request=request,
        name="quiz.html",
        context={"user": user, "questions": QUESTIONS, "total": len(QUESTIONS)}
    )


class QuizSubmit(BaseModel):
    answers: dict  # {question_id: answer_index}


@router.post("/submit")
def submit_quiz(
    data: QuizSubmit,
    db: Session = Depends(get_db),
    access_token: Optional[str] = Cookie(default=None)
):
    """Принимает ответы, определяет уровень, сохраняет результат."""
    user = get_current_user(db, access_token)
    if not user:
        raise HTTPException(status_code=401, detail="Необходима авторизация")

    # Определяем уровень
    level, score = determine_level(data.answers)

    # Сохраняем результат
    result = DiagnosticResult(
        user_id=user.id,
        level=level,
        score=score,
        answers=json.dumps(data.answers)
    )
    db.add(result)

    # Обновляем уровень пользователя
    user.level = level
    db.commit()

    return {"level": level, "score": score}


@router.get("/result")
async def quiz_result(
    request: Request,
    db: Session = Depends(get_db),
    access_token: Optional[str] = Cookie(default=None)
):
    """Страница результатов теста."""
    user = get_current_user(db, access_token)
    if not user:
        return RedirectResponse(url="/login")

    result = db.query(DiagnosticResult).filter(
        DiagnosticResult.user_id == user.id
    ).first()

    if not result:
        return RedirectResponse(url="/quiz")

    recommendations = get_recommendations(result.level)

    return templates.TemplateResponse(
        request=request,
        name="quiz_result.html",
        context={
            "user": user,
            "result": result,
            "recommendations": recommendations
        }
    )


@router.post("/reset")
def reset_quiz(
    db: Session = Depends(get_db),
    access_token: Optional[str] = Cookie(default=None)
):
    """Сбрасывает результат теста (для повторного прохождения)."""
    user = get_current_user(db, access_token)
    if not user:
        raise HTTPException(status_code=401, detail="Необходима авторизация")

    db.query(DiagnosticResult).filter(
        DiagnosticResult.user_id == user.id
    ).delete()
    db.commit()
    return {"message": "Тест сброшен"}