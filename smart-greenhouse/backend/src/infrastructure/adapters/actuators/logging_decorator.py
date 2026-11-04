from uuid import UUID

from src.domain.actuators.ports import ActuatorPort
from src.infrastructure.adapters.actuators.max_runtime_decorator import (
    PolicyBlockedError,
)
from src.infrastructure.persistence.execution_log_repository import (
    ExecutionLogRepository,
)


class LoggingActuatorDecorator(ActuatorPort):
    def __init__(
        self,
        inner: ActuatorPort,
        execution_log_repository: ExecutionLogRepository,
    ):
        self.inner = inner
        self.execution_log_repository = (
            execution_log_repository
        )

    def apply(
        self,
        device_id: UUID,
        command: str,
        payload: dict,
    ) -> None:
        try:
            self.inner.apply(
                device_id=device_id,
                command=command,
                payload=payload,
            )

        except PolicyBlockedError as exc:
            self.execution_log_repository.create(
                device_id=device_id,
                success=False,
                policy_applied=[
                    exc.policy_name,
                    "logging",
                ],
                message=str(exc),
            )

            raise

        except Exception as exc:
            self.execution_log_repository.create(
                device_id=device_id,
                success=False,
                policy_applied=[
                    "logging",
                ],
                message=str(exc),
            )

            raise

        self.execution_log_repository.create(
            device_id=device_id,
            success=True,
            policy_applied=[
                "logging",
            ],
            message=None,
        )