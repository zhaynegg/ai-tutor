import uuid
import traceback
from fastapi import APIRouter, Depends, Cookie, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.schemas import GenerateTaskRequest, TaskResponse
from app.services.ai_service import ai_service
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/generate_task", response_model=TaskResponse)
def generate_task(
    request: GenerateTaskRequest,
    db: Session = Depends(get_db),
    access_token: Optional[str] = Cookie(default=None)
):
    if not get_current_user(db, access_token):
        raise HTTPException(status_code=401, detail="Необходима авторизация")
    try:
        result = ai_service.generate_task(
            topic=request.topic,
            difficulty=request.difficulty,
            language=request.language
        )
        return TaskResponse(
            task_id=str(uuid.uuid4()),
            title=result.get("title", "Задание"),
            description=result.get("description", ""),
            difficulty=request.difficulty,
            hints=result.get("hints", []),
            expected_output=result.get("expected_output", "")
        )
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))