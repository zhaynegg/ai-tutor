from typing import Optional
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.auth_service import get_current_user
import traceback
from fastapi import APIRouter, HTTPException, Cookie, Depends
from app.models.schemas import ExplainErrorRequest, ExplainErrorResponse
from app.services.ai_service import ai_service

router = APIRouter(prefix="/explainer", tags=["Explainer"])


@router.post("/explain_error", response_model=ExplainErrorResponse)
def explain_error(request: ExplainErrorRequest, db: Session = Depends(get_db), access_token: Optional[str] = Cookie(default=None)):
    if not get_current_user(db, access_token):
        raise HTTPException(status_code=401, detail="Необходима авторизация")
    try:
        result = ai_service.explain_error(
            code=request.code,
            error=request.error_message,
            level=request.student_level
        )
        return ExplainErrorResponse(
            error_type=result.get("error_type", "Error"),
            explanation=result.get("explanation", ""),
            fix_suggestion=result.get("fix_suggestion", ""),
            example=result.get("example", "")
        )
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))