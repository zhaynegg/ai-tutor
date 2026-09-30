from fastapi import FastAPI, Request, Cookie, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional

from app.config import settings, PROJECT_ROOT
from app.database import engine, Base, SessionLocal, get_db
from app.models import db_models
from app.models.db_models import Course, LessonProgress
from app.routers import tasks, checker, explainer, auth, chat, courses, quiz, admin, password
from app.services.auth_service import get_current_user

# Создаём таблицы в БД при старте
Base.metadata.create_all(bind=engine)

# Заполняем БД готовыми курсами при первом запуске
from app.services.course_service import seed_courses
_db = SessionLocal()
try:
    seed_courses(_db)
finally:
    _db.close()

# Создаём приложение
app = FastAPI(title=settings.APP_TITLE, version=settings.APP_VERSION)

app.mount("/static", StaticFiles(directory=str(PROJECT_ROOT / "static")), name="static")
templates = Jinja2Templates(directory=str(PROJECT_ROOT / "templates"))

# Подключаем роутеры
app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(checker.router)
app.include_router(explainer.router)
app.include_router(chat.router)
app.include_router(courses.router)
app.include_router(quiz.router)
app.include_router(admin.router)
app.include_router(password.router)

def get_user(token: Optional[str] = None):
    """Получает пользователя из cookie."""
    if not token:
        return None
    db = SessionLocal()
    try:
        return get_current_user(db, token)
    finally:
        db.close()


# ── МАРШРУТЫ СТРАНИЦ ──────────────────────────────

@app.get("/")
async def index(
    request: Request,
    db: Session = Depends(get_db),
    access_token: Optional[str] = Cookie(default=None)
):
    user = get_user(access_token)

    # Если не авторизован — на страницу входа
    if not user:
        return RedirectResponse(url="/login")

    all_courses = db.query(Course).order_by(Course.order).all()
    courses_with_progress = []
    for course in all_courses:
        total_lessons = len(course.lessons)
        done_lessons = 0
        done_lessons = db.query(LessonProgress).filter(
            LessonProgress.user_id == user.id,
            LessonProgress.lesson_id.in_([l.id for l in course.lessons]),
            LessonProgress.is_done == True
        ).count()
        courses_with_progress.append({
            "course": course,
            "total": total_lessons,
            "done": done_lessons,
            "percent": int(done_lessons / total_lessons * 100) if total_lessons > 0 else 0
        })

    return templates.TemplateResponse(
        request=request,
        name="courses.html",
        context={"user": user, "courses": courses_with_progress}
    )

@app.get("/coding")
async def coding_page(
    request: Request,
    access_token: Optional[str] = Cookie(default=None)
):
    """Страница свободного кодинга с AI."""
    user = get_user(access_token)
    return templates.TemplateResponse(
        request=request, name="index.html", context={"user": user}
    )


@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="login.html", context={}
    )


@app.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="register.html", context={}
    )

@app.get("/verify-email")
async def verify_email_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="verify_email.html", context={}
    )


@app.get("/dashboard")
async def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    access_token: Optional[str] = Cookie(default=None)
):
    user = get_user(access_token)
    if not user:
        return RedirectResponse(url="/login")

    attempts = db.query(db_models.Attempt)\
        .filter(db_models.Attempt.user_id == user.id)\
        .order_by(db_models.Attempt.created_at.desc())\
        .limit(10).all()

    total = db.query(db_models.Attempt)\
        .filter(db_models.Attempt.user_id == user.id).count()

    correct = db.query(db_models.Attempt)\
        .filter(db_models.Attempt.user_id == user.id,
                db_models.Attempt.is_correct == True).count()

    scores = db.query(db_models.Attempt.score)\
        .filter(db_models.Attempt.user_id == user.id).all()

    avg_score = round(
        sum(s[0] for s in scores) / len(scores), 1
    ) if scores else 0

    topics = list(set(
        a.topic for a in db.query(db_models.Attempt)
        .filter(db_models.Attempt.user_id == user.id).all()
    ))

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "user": user,
            "attempts": attempts,
            "total": total,
            "correct": correct,
            "avg_score": avg_score,
            "topics": topics
        }
    )


@app.get("/chat")
async def chat_page(
    request: Request,
    access_token: Optional[str] = Cookie(default=None)
):
    user = get_user(access_token)
    return templates.TemplateResponse(
        request=request, name="chat.html", context={"user": user}
    )

@app.get("/admin/")
async def admin_page(
    request: Request,
    access_token: Optional[str] = Cookie(default=None)
):
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/admin")

@app.get("/quiz")
async def quiz_page_redirect(
    request: Request,
    access_token: Optional[str] = Cookie(default=None)
):
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/quiz/")

@app.get("/health")
def health():
    return {"status": "ok", "version": settings.APP_VERSION}