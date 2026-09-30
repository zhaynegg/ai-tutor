from app.config import PROJECT_ROOT
from fastapi import APIRouter, Depends, Cookie, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.models.db_models import Course, Lesson, LessonProgress
from app.services.auth_service import get_current_user
from app.services.ai_service import ai_service
from app.services.code_runner import code_runner

router = APIRouter(prefix="/courses", tags=["Courses"])
templates = Jinja2Templates(directory=str(PROJECT_ROOT / "templates"))


@router.get("")
async def courses_list(
    request: Request,
    db: Session = Depends(get_db),
    access_token: Optional[str] = Cookie(default=None)
):
    """Список всех курсов."""
    user = get_current_user(db, access_token)
    courses = db.query(Course).order_by(Course.order).all()

    # Считаем прогресс для каждого курса
    courses_with_progress = []
    for course in courses:
        total_lessons = len(course.lessons)
        done_lessons = 0

        if user:
            done_lessons = db.query(LessonProgress).filter(
                LessonProgress.user_id == user.id,
                LessonProgress.lesson_id.in_(
                    [l.id for l in course.lessons]
                ),
                LessonProgress.is_done == True
            ).count()

        courses_with_progress.append({
            "course": course,
            "total": total_lessons,
            "done": done_lessons,
            "percent": int(done_lessons / total_lessons * 100)
                       if total_lessons > 0 else 0
        })

    return templates.TemplateResponse(
        request=request,
        name="courses.html",
        context={"user": user, "courses": courses_with_progress}
    )


@router.get("/{course_id}")
async def course_detail(
    request: Request,
    course_id: int,
    db: Session = Depends(get_db),
    access_token: Optional[str] = Cookie(default=None)
):
    """Страница курса со списком уроков."""
    user = get_current_user(db, access_token)
    course = db.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")

    # Прогресс по каждому уроку
    lessons_with_progress = []
    for lesson in course.lessons:
        progress = None
        if user:
            progress = db.query(LessonProgress).filter(
                LessonProgress.user_id == user.id,
                LessonProgress.lesson_id == lesson.id
            ).first()

        lessons_with_progress.append({
            "lesson": lesson,
            "is_done": progress.is_done if progress else False,
            "score": progress.score if progress else 0
        })

    return templates.TemplateResponse(
        request=request,
        name="course_detail.html",
        context={
            "user": user,
            "course": course,
            "lessons": lessons_with_progress
        }
    )


@router.get("/{course_id}/lessons/{lesson_id}")
async def lesson_page(
    request: Request,
    course_id: int,
    lesson_id: int,
    db: Session = Depends(get_db),
    access_token: Optional[str] = Cookie(default=None)
):
    """Страница урока с теорией и заданием."""
    user = get_current_user(db, access_token)
    lesson = db.query(Lesson).filter(
        Lesson.id == lesson_id,
        Lesson.course_id == course_id
    ).first()

    if not lesson:
        raise HTTPException(status_code=404, detail="Урок не найден")

    # Прогресс по этому уроку
    progress = None
    if user:
        progress = db.query(LessonProgress).filter(
            LessonProgress.user_id == user.id,
            LessonProgress.lesson_id == lesson_id
        ).first()

    # Следующий урок
    next_lesson = db.query(Lesson).filter(
        Lesson.course_id == course_id,
        Lesson.order > lesson.order
    ).order_by(Lesson.order).first()

    return templates.TemplateResponse(
        request=request,
        name="lesson.html",
        context={
            "user": user,
            "lesson": lesson,
            "course_id": course_id,
            "progress": progress,
            "next_lesson": next_lesson
        }
    )


class CheckLessonCode(BaseModel):
    lesson_id: int
    course_id: int
    code: str


@router.post("/check_lesson")
def check_lesson_code(
    data: CheckLessonCode,
    db: Session = Depends(get_db),
    access_token: Optional[str] = Cookie(default=None)
):
    """Проверяет код задания урока и сохраняет прогресс."""
    user = get_current_user(db, access_token)
    if not user:
        raise HTTPException(status_code=401, detail="Необходима авторизация")

    lesson = db.query(Lesson).filter(Lesson.id == data.lesson_id, Lesson.course_id == data.course_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Урок не найден")

    # Запускаем код
    success, stdout, stderr = code_runner.run(data.code)
    execution_result = stdout if success else stderr

    # AI проверяет код
    result = ai_service.check_code(
        task=lesson.task,
        code=data.code
    )

    score = result.get("score", 0)
    is_correct = result.get("is_correct", False)

    # Сохраняем прогресс если пользователь авторизован
    if user:
        progress = db.query(LessonProgress).filter(
            LessonProgress.user_id == user.id,
            LessonProgress.lesson_id == data.lesson_id
        ).first()

        if progress:
            # Обновляем если новый балл выше
            if score > progress.score:
                progress.score = score
                progress.is_done = is_correct
        else:
            progress = LessonProgress(
                user_id=user.id,
                lesson_id=data.lesson_id,
                is_done=is_correct,
                score=score
            )
            db.add(progress)
        db.commit()

    return {
        "is_correct": is_correct,
        "score": score,
        "feedback": result.get("feedback", ""),
        "suggestions": result.get("suggestions", []),
        "execution_result": execution_result
    }