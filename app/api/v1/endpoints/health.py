from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.common import ApiResponse
from app.utils.responses import success_response

router = APIRouter()


@router.get("/", response_model=ApiResponse)
def health_check(db: Session = Depends(get_db)) -> dict:
    database_status = "disconnected"

    try:
        db.execute(text("SELECT 1"))
        database_status = "connected"
    except Exception:
        database_status = "disconnected"

    return success_response(
        message="Health check completed.",
        data={"api": "ok", "database": database_status},
    )
