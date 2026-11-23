from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.application.alerts.setup import (
    build_event_bus,
)
from src.application.actuators.service import (
    ActuatorStateService,
)
from src.domain.actuators.state import (
    IllegalTransitionError,
)
from src.infrastructure.db import (
    get_db,
)
from src.infrastructure.persistence.actuator_state_repository import (
    ActuatorStateRepository,
)


router = APIRouter(
    prefix="/api/devices",
    tags=["actuator-state"],
)


class ActuatorStateResponse(BaseModel):
    state: str
    allowed_commands: list[str]


class TransitionRequest(BaseModel):
    target: str


def build_service(
    db: Session,
) -> ActuatorStateService:
    return ActuatorStateService(
        repository=ActuatorStateRepository(
            db
        ),
        event_bus=build_event_bus(
            db
        ),
    )


@router.get(
    "/{device_id}/state",
    response_model=ActuatorStateResponse,
)
def get_actuator_state(
    device_id: UUID,
    db: Session = Depends(get_db),
):
    service = build_service(
        db
    )

    try:
        context = service.get_state(
            device_id
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    return ActuatorStateResponse(
        state=context.state,
        allowed_commands=(
            context.allowed_commands
        ),
    )


@router.post(
    "/{device_id}/transition",
    response_model=ActuatorStateResponse,
)
def transition_actuator_state(
    device_id: UUID,
    request: TransitionRequest,
    db: Session = Depends(get_db),
):
    service = build_service(
        db
    )

    try:
        context = service.transition(
            device_id=device_id,
            target_state=request.target,
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except IllegalTransitionError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return ActuatorStateResponse(
        state=context.state,
        allowed_commands=(
            context.allowed_commands
        ),
    )