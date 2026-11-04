from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from src.application.actuators.execution_dto import (
    ActuatorApplyRequest,
    ActuatorExecutionDto,
)
from src.application.actuators.execution_service import (
    ActuatorExecutionService,
)
from src.infrastructure.adapters.actuators.logging_decorator import (
    LoggingActuatorDecorator,
)
from src.infrastructure.adapters.actuators.max_runtime_decorator import (
    MaxRuntimeActuatorDecorator,
    PolicyBlockedError,
)
from src.infrastructure.adapters.actuators.simulation import (
    SimulationActuatorAdapter,
)
from src.infrastructure.db import get_db
from src.infrastructure.persistence.actuator_state_repository import (
    ActuatorStateRepository,
)
from src.infrastructure.persistence.execution_log_repository import (
    ExecutionLogRepository,
)


router = APIRouter(
    prefix="/api/actuators",
    tags=["actuators"],
)


def build_execution_service(
    db: Session,
) -> ActuatorExecutionService:
    execution_repository = (
        ExecutionLogRepository(db)
    )

    state_repository = (
        ActuatorStateRepository(db)
    )

    # Innermost component
    simulation_adapter = (
        SimulationActuatorAdapter()
    )

    # Middle decorator
    max_runtime = (
        MaxRuntimeActuatorDecorator(
            inner=simulation_adapter,
            state_repository=state_repository,
        )
    )

    # Outermost decorator
    logging = LoggingActuatorDecorator(
        inner=max_runtime,
        execution_log_repository=(
            execution_repository
        ),
    )

    return ActuatorExecutionService(
        actuator_port=logging,
        execution_log_repository=(
            execution_repository
        ),
    )


@router.get(
    "/executions",
    response_model=list[
        ActuatorExecutionDto
    ],
)
def list_executions(
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
) -> list[ActuatorExecutionDto]:
    service = build_execution_service(
        db
    )

    return service.list_recent(
        limit=limit
    )


@router.post(
    "/{device_id}/apply",
    status_code=status.HTTP_200_OK,
)
def apply_actuator(
    device_id: UUID,
    request: ActuatorApplyRequest,
    db: Session = Depends(get_db),
):
    state_repository = (
        ActuatorStateRepository(db)
    )

    actuator = (
        state_repository.get_actuator(
            device_id
        )
    )

    if actuator is None:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail="Actuator not found",
        )

    service = build_execution_service(
        db
    )

    try:
        service.apply(
            device_id=device_id,
            command=request.command,
            payload=request.payload,
        )

    except PolicyBlockedError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=str(exc),
        ) from exc

    return {
        "status": "applied",
        "device_id": str(device_id),
        "command": request.command,
    }