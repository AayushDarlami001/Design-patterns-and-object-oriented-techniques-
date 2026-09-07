from fastapi import APIRouter

from src.infrastructure.db import check_database_connection


router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    db_status = "ok" if check_database_connection() else "fail"
    overall_status = "ok" if db_status == "ok" else "degraded"

    return {
        "status": overall_status,
        "db": db_status,
    }