from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# ── AI запросы ──────────────────────────────────────

class GenerateTaskRequest(BaseModel):
    topic: str
    difficulty: str
    language: str = "Python"

class CheckCodeRequest(BaseModel):
    task_description: str
    student_code: str
    topic: str = ""
    difficulty: str = "beginner"
    task_title: str = ""

class ExplainErrorRequest(BaseModel):
    code: str
    error_message: str
    student_level: str = "beginner"

# ── AI ответы ───────────────────────────────────────

class TaskResponse(BaseModel):
    task_id: str
    title: str
    description: str
    difficulty: str
    hints: list[str]
    expected_output: str

class CheckCodeResponse(BaseModel):
    is_correct: bool
    score: int
    feedback: str
    execution_result: Optional[str] = None
    suggestions: list[str] = []

class ExplainErrorResponse(BaseModel):
    error_type: str
    explanation: str
    fix_suggestion: str
    example: str

# ── Авторизация ─────────────────────────────────────

class UserRegister(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=r"^[\w.-]+$")
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)
    full_name: str = ""

class UserLogin(BaseModel):
    username: str
    password: str

# ── Статистика ──────────────────────────────────────

class AttemptOut(BaseModel):
    id: int
    topic: str
    difficulty: str
    task_title: str
    score: float
    is_correct: bool
    created_at: datetime

    class Config:
        from_attributes = True