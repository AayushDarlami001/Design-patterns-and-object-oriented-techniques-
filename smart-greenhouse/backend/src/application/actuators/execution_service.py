from uuid import UUID

from src.application.actuators.execution_dto import (
    ActuatorExecutionDto,
)
from src.domain.actuators.ports import ActuatorPort
from src.infrastructure.persistence.execution_log_repository import (
    ExecutionLogRepository,
)


class ActuatorExecutionService:
    def __init__(
        self,
        actuator_port: ActuatorPort,
        execution_log_repository: ExecutionLogRepository,
    ):
        self.actuator_port = actuator_port
        self.execution_log_repository = (
            execution_log_repository
        )

    def apply(
        self,
        device_id: UUID,
        command: str,
        payload: dict,
    ) -> None:
        self.actuator_port.apply(
            device_id=device_id,
            command=command,
            payload=payload,
        )

    def list_recent(
        self,
        limit: int = 20,
    ) -> list[ActuatorExecutionDto]:
        rows = (
            self.execution_log_repository.list_recent(
                limit=limit
            )
        )

        return [
            ActuatorExecutionDto(
                id=row.id,
                device_id=row.device_id,
                success=row.success,
                policy_applied=(
                    row.policy_applied
                ),
                message=row.message,
                created_at=row.created_at,
            )
            for row in rows
        ]