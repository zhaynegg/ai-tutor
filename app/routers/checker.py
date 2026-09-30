import traceback
from fastapi import APIRouter, Depends, Cookie, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.schemas import CheckCodeRequest, CheckCodeResponse
from app.models.db_models import Attempt
from app.services.ai_service import ai_service
from app.services.code_runner import code_runner
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/checker", tags=["Checker"])


@router.post("/check_code", response_model=CheckCodeResponse)
def check_code(
    request: CheckCodeRequest,
    db: Session = Depends(get_db),
    access_token: Optional[str] = Cookie(default=None)
):
    if not get_current_user(db, access_token):
        raise HTTPException(status_code=401, detail="Необходима авторизация")
    # Шаг 1: запускаем код
    success, stdout, stderr = code_runner.run(request.student_code)
    execution_result = stdout if success else stderr

    try:
        # Шаг 2: AI проверяет
        result = ai_service.check_code(
            task=request.task_description,
            code=request.student_code
        )

        # Шаг 3: сохраняем попытку если пользователь авторизован
        user = get_current_user(db, access_token)
        if user:
            attempt = Attempt(
                user_id=user.id,
                topic=request.topic or "Общее",
                difficulty=request.difficulty or "beginner",
                task_title=request.task_title or "Задание",
                student_code=request.student_code,
                score=result.get("score", 0),
                is_correct=result.get("is_correct", False),
                feedback=result.get("feedback", "")
            )
            db.add(attempt)
            db.commit()

        return CheckCodeResponse(
            is_correct=result.get("is_correct", success),
            score=result.get("score", 0),
            feedback=result.get("feedback", ""),
            execution_result=execution_result,
            suggestions=result.get("suggestions", [])
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))