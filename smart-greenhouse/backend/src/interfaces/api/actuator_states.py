from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from src.application.actuators.dto import (
    ActuatorStateDto,
    ActuatorTransitionRequest,
)
from src.application.actuators.service import (
    ActuatorStateService,
)
from src.domain.actuators.state import (
    IllegalTransitionError,
)
from src.infrastructure.db import SessionLocal
from src.infrastructure.persistence.actuator_state_repository import (
    ActuatorStateRepository,
)


router = APIRouter(
    prefix="/api/devices",
    tags=["actuator-state"],
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def get_service(
    db: Session = Depends(get_db),
) -> ActuatorStateService:
    repository = ActuatorStateRepository(
        db
    )

    return ActuatorStateService(
        repository
    )


@router.get(
    "/{device_id}/state",
    response_model=ActuatorStateDto,
)
def get_actuator_state(
    device_id: UUID,
    service: ActuatorStateService = Depends(
        get_service
    ),
):
    try:
        context = service.get_state(
            device_id
        )

        return ActuatorStateDto(
            state=context.state,
            allowed_commands=(
                context.allowed_commands
            ),
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=str(exc),
        ) from exc


@router.post(
    "/{device_id}/transition",
    response_model=ActuatorStateDto,
)
def transition_actuator(
    device_id: UUID,
    request: ActuatorTransitionRequest,
    service: ActuatorStateService = Depends(
        get_service
    ),
):
    try:
        context = service.transition(
            device_id=device_id,
            target_state=request.target,
        )

        return ActuatorStateDto(
            state=context.state,
            allowed_commands=(
                context.allowed_commands
            ),
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=str(exc),
        ) from exc

    except IllegalTransitionError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=str(exc),
        ) from exc