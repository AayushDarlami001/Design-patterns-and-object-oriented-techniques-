from sqlalchemy.orm import Session

from src.domain.actuators.ports import ActuatorPort
from src.infrastructure.adapters.actuators.logging_decorator import (
    LoggingActuatorDecorator,
)
from src.infrastructure.adapters.actuators.max_runtime_decorator import (
    MaxRuntimeActuatorDecorator,
)
from src.infrastructure.adapters.actuators.simulation import (
    SimulationActuatorAdapter,
)
from src.infrastructure.persistence.actuator_state_repository import (
    ActuatorStateRepository,
)
from src.infrastructure.persistence.execution_log_repository import (
    ExecutionLogRepository,
)


def build_actuator_port(
    db: Session,
) -> ActuatorPort:
    execution_repository = (
        ExecutionLogRepository(db)
    )

    state_repository = (
        ActuatorStateRepository(db)
    )

    simulation_adapter = (
        SimulationActuatorAdapter()
    )

    max_runtime = (
        MaxRuntimeActuatorDecorator(
            inner=simulation_adapter,
            state_repository=state_repository,
        )
    )

    logging = LoggingActuatorDecorator(
        inner=max_runtime,
        execution_log_repository=(
            execution_repository
        ),
    )

    return logging