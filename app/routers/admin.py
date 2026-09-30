from app.config import PROJECT_ROOT
from fastapi import APIRouter, Depends, Cookie, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.models.db_models import User, Course, Lesson, Attempt, LessonProgress
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/admin", tags=["Admin"])
templates = Jinja2Templates(directory=str(PROJECT_ROOT / "templates"))


def require_admin(db: Session, token: Optional[str]) -> User:
    """Проверяет что пользователь — администратор."""
    user = get_current_user(db, token)
    if not user:
        raise HTTPException(status_code=401, detail="Необходима авторизация")
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Доступ запрещён")
    return user


# ── ГЛАВНАЯ СТРАНИЦА АДМИНКИ ──────────────────────

@router.get("")
async def admin_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    access_token: Optional[str] = Cookie(default=None)
):
    """Главная страница админ панели."""
    try:
        user = require_admin(db, access_token)
    except HTTPException:
        return RedirectResponse(url="/login")

    # Статистика
    total_users    = db.query(User).count()
    total_courses  = db.query(Course).count()
    total_lessons  = db.query(Lesson).count()
    total_attempts = db.query(Attempt).count()

    # Последние зарегистрированные пользователи
    recent_users = db.query(User)\
        .order_by(User.created_at.desc())\
        .limit(5).all()

    return templates.TemplateResponse(
        request=request,
        name="admin/dashboard.html",
        context={
            "user": user,
            "total_users": total_users,
            "total_courses": total_courses,
            "total_lessons": total_lessons,
            "total_attempts": total_attempts,
            "recent_users": recent_users
        }
    )


# ── ПОЛЬЗОВАТЕЛИ ──────────────────────────────────

@router.get("/users")
async def admin_users(
    request: Request,
    db: Session = Depends(get_db),
    access_token: Optional[str] = Cookie(default=None)
):
    """Список всех пользователей."""
    try:
        user = require_admin(db, access_token)
    except HTTPException:
        return RedirectResponse(url="/login")

    users = db.query(User).order_by(User.created_at.desc()).all()

    # Добавляем статистику для каждого пользователя
    users_data = []
    for u in users:
        attempts_count = db.query(Attempt).filter(Attempt.user_id == u.id).count()
        correct_count = db.query(Attempt).filter(
            Attempt.user_id == u.id,
            Attempt.is_correct == True
        ).count()
        users_data.append({
            "user": u,
            "attempts": attempts_count,
            "correct": correct_count
        })

    return templates.TemplateResponse(
        request=request,
        name="admin/users.html",
        context={"user": user, "users_data": users_data}
    )


@router.post("/users/{user_id}/toggle_admin")
def toggle_admin(
    user_id: int,
    db: Session = Depends(get_db),
    access_token: Optional[str] = Cookie(default=None)
):
    """Выдаёт или забирает права администратора."""
    require_admin(db, access_token)
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    target.is_admin = not target.is_admin
    db.commit()
    return {"is_admin": target.is_admin}


@router.post("/users/{user_id}/delete")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    access_token: Optional[str] = Cookie(default=None)
):
    """Удаляет пользователя и все его данные."""
    require_admin(db, access_token)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    from app.models.db_models import DiagnosticResult, PasswordResetCode
    from sqlalchemy import text

    # Удаляем все связанные данные
    db.query(Attempt).filter(Attempt.user_id == user_id).delete()
    db.query(LessonProgress).filter(LessonProgress.user_id == user_id).delete()
    db.query(DiagnosticResult).filter(DiagnosticResult.user_id == user_id).delete()
    db.query(PasswordResetCode).filter(PasswordResetCode.user_id == user_id).delete()

    # email_verifications удаляем через text т.к. модель может отсутствовать
    try:
        db.execute(text(f"DELETE FROM email_verifications WHERE user_id = {user_id}"))
    except Exception:
        pass

    db.delete(user)
    db.commit()
    return {"message": "Пользователь удалён"}


# ── КУРСЫ ─────────────────────────────────────────

@router.get("/courses")
async def admin_courses(
    request: Request,
    db: Session = Depends(get_db),
    access_token: Optional[str] = Cookie(default=None)
):
    """Список всех курсов."""
    try:
        user = require_admin(db, access_token)
    except HTTPException:
        return RedirectResponse(url="/login")

    courses = db.query(Course).order_by(Course.order).all()
    courses_data = []
    for c in courses:
        courses_data.append({
            "course": c,
            "lessons_count": len(c.lessons)
        })

    return templates.TemplateResponse(
        request=request,
        name="admin/courses.html",
        context={"user": user, "courses_data": courses_data}
    )


class CourseCreate(BaseModel):
    title: str
    description: str
    icon: str = "📚"
    order: int = 0


@router.post("/courses/create")
def create_course(
    data: CourseCreate,
    db: Session = Depends(get_db),
    access_token: Optional[str] = Cookie(default=None)
):
    """Создаёт новый курс."""
    require_admin(db, access_token)
    course = Course(
        title=data.title,
        description=data.description,
        icon=data.icon,
        order=data.order
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return {"id": course.id, "title": course.title}


@router.post("/courses/{course_id}/delete")
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    access_token: Optional[str] = Cookie(default=None)
):
    """Удаляет курс и все его уроки."""
    require_admin(db, access_token)
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")

    # Удаляем уроки и прогресс
    for lesson in course.lessons:
        db.query(LessonProgress).filter(
            LessonProgress.lesson_id == lesson.id
        ).delete()
        db.delete(lesson)

    db.delete(course)
    db.commit()
    return {"message": "Курс удалён"}


# ── УРОКИ ─────────────────────────────────────────

@router.get("/courses/{course_id}/edit")
async def edit_course(
    request: Request,
    course_id: int,
    db: Session = Depends(get_db),
    access_token: Optional[str] = Cookie(default=None)
):
    """Страница редактирования курса и его уроков."""
    try:
        user = require_admin(db, access_token)
    except HTTPException:
        return RedirectResponse(url="/login")

    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")

    return templates.TemplateResponse(
        request=request,
        name="admin/course_edit.html",
        context={"user": user, "course": course}
    )


class LessonCreate(BaseModel):
    title: str
    theory: str = ""
    code_example: str = ""
    task: str = ""
    expected_output: str = ""
    order: int = 0


@router.post("/courses/{course_id}/lessons/create")
def create_lesson(
    course_id: int,
    data: LessonCreate,
    db: Session = Depends(get_db),
    access_token: Optional[str] = Cookie(default=None)
):
    """Создаёт новый урок в курсе."""
    require_admin(db, access_token)
    lesson = Lesson(
        course_id=course_id,
        title=data.title,
        theory=data.theory,
        code_example=data.code_example,
        task=data.task,
        expected_output=data.expected_output,
        order=data.order
    )
    db.add(lesson)
    db.commit()
    db.refresh(lesson)
    return {"id": lesson.id, "title": lesson.title}


@router.post("/lessons/{lesson_id}/delete")
def delete_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    access_token: Optional[str] = Cookie(default=None)
):
    """Удаляет урок."""
    require_admin(db, access_token)
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Урок не найден")

    db.query(LessonProgress).filter(
        LessonProgress.lesson_id == lesson_id
    ).delete()
    db.delete(lesson)
    db.commit()
    return {"message": "Урок удалён"}