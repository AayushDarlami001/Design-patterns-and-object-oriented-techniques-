from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from src.application.automation.dto import (
    AutomationEvaluationDto,
    StrategyDto,
    StrategyUpdateRequest,
)
from src.application.automation.service import (
    AutomationService,
)
from src.infrastructure.db import SessionLocal
from src.infrastructure.persistence.automation_repository import (
    AutomationRepository,
)


router = APIRouter(
    prefix="/api/locations",
    tags=["automation"],
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def get_service(
    db: Session = Depends(get_db),
) -> AutomationService:
    repository = AutomationRepository(db)

    return AutomationService(
        repository=repository,
    )


@router.get(
    "/{location_id}/automation",
    response_model=StrategyDto,
)
def get_location_strategy(
    location_id: UUID,
    service: AutomationService = Depends(
        get_service
    ),
):
    try:
        return service.get_strategy(
            location_id
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.put(
    "/{location_id}/automation",
    response_model=StrategyDto,
)
def save_location_strategy(
    location_id: UUID,
    body: StrategyUpdateRequest,
    service: AutomationService = Depends(
        get_service
    ),
):
    try:
        return service.save_strategy(
            location_id=location_id,
            strategy_key=body.strategy_key,
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post(
    "/{location_id}/automation/evaluate",
    response_model=AutomationEvaluationDto,
)
def evaluate_location(
    location_id: UUID,
    service: AutomationService = Depends(
        get_service
    ),
):
    try:
        return service.evaluate(
            location_id
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc