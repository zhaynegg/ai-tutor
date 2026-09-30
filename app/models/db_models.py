from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id              = Column(Integer, primary_key=True, index=True)
    username        = Column(String, unique=True, nullable=False)
    email           = Column(String, unique=True, nullable=False)
    full_name       = Column(String, default="")
    hashed_password = Column(String, nullable=False)
    role            = Column(String, default="student")
    level           = Column(String, default="beginner")
    is_active       = Column(Boolean, default=True)
    is_admin        = Column(Boolean, default=False)
    created_at      = Column(DateTime, default=datetime.utcnow)

    attempts         = relationship("Attempt", back_populates="user")
    lesson_progress  = relationship("LessonProgress", back_populates="user")
    diagnostic_results = relationship("DiagnosticResult", back_populates="user")
    is_verified = Column(Boolean, default=False)


class Course(Base):
    __tablename__ = "courses"

    id          = Column(Integer, primary_key=True, index=True)
    title       = Column(String, nullable=False)
    description = Column(Text, default="")
    icon        = Column(String, default="📚")
    difficulty  = Column(String, default="beginner")
    order       = Column(Integer, default=0)
    created_at  = Column(DateTime, default=datetime.utcnow)

    lessons = relationship("Lesson", back_populates="course",
                          order_by="Lesson.order", cascade="all, delete")


class Lesson(Base):
    __tablename__ = "lessons"

    id              = Column(Integer, primary_key=True, index=True)
    course_id       = Column(Integer, ForeignKey("courses.id"), nullable=False)
    title           = Column(String, nullable=False)
    theory          = Column(Text, default="")
    code_example    = Column(Text, default="")
    task            = Column(Text, default="")
    expected_output = Column(Text, default="")
    order           = Column(Integer, default=0)
    created_at      = Column(DateTime, default=datetime.utcnow)

    course   = relationship("Course", back_populates="lessons")
    progress = relationship("LessonProgress", back_populates="lesson")


class LessonProgress(Base):
    __tablename__ = "lesson_progress"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    lesson_id  = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    is_done    = Column(Boolean, default=False)
    score      = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    user   = relationship("User", back_populates="lesson_progress")
    lesson = relationship("Lesson", back_populates="progress")


class Attempt(Base):
    __tablename__ = "attempts"

    id           = Column(Integer, primary_key=True, index=True)
    user_id      = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic        = Column(String, default="")
    difficulty   = Column(String, default="")
    task_title   = Column(String, default="")
    student_code = Column(Text, default="")
    score        = Column(Float, default=0)
    is_correct   = Column(Boolean, default=False)
    feedback     = Column(Text, default="")
    created_at   = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="attempts")


class DiagnosticResult(Base):
    __tablename__ = "diagnostic_results"

    id              = Column(Integer, primary_key=True, index=True)
    user_id         = Column(Integer, ForeignKey("users.id"), nullable=False)
    level           = Column(String, default="beginner")
    score           = Column(Float, default=0)
    answers         = Column(Text, default="{}")
    weak_topics     = Column(Text, default="")
    strong_topics   = Column(Text, default="")
    recommendations = Column(Text, default="")
    created_at      = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="diagnostic_results")


class PasswordResetCode(Base):
    __tablename__ = "password_reset_codes"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=True)
    email      = Column(String, nullable=False)
    code       = Column(String, nullable=False)
    is_used    = Column(Boolean, default=False)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class GeneratedTask(Base):
    __tablename__ = "generated_tasks"

    id         = Column(Integer, primary_key=True, index=True)
    topic      = Column(String)
    difficulty = Column(String)
    task_text  = Column(Text)
    solution   = Column(Text)
    seed       = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class EmailVerification(Base):
    """Коды подтверждения email."""
    __tablename__ = "email_verifications"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    code       = Column(String, nullable=False)
    is_used    = Column(Boolean, default=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)