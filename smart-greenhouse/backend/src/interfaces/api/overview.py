from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from src.application.overview.dto import (
    LocationOverviewDto,
)
from src.application.overview.facade import (
    LocationOverviewFacade,
)
from src.infrastructure.db import SessionLocal


router = APIRouter(
    prefix="/api/locations",
    tags=["overview"],
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def get_overview_facade(
    db: Session = Depends(get_db),
) -> LocationOverviewFacade:
    return LocationOverviewFacade(
        db
    )


@router.get(
    "/{location_id}/overview",
    response_model=LocationOverviewDto,
)
def get_location_overview(
    location_id: UUID,
    facade: LocationOverviewFacade = Depends(
        get_overview_facade
    ),
):
    try:
        return facade.get_overview(
            location_id
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=str(exc),
        ) from exc