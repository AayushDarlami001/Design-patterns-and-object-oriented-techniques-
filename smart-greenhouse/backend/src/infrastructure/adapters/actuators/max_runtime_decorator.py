from datetime import datetime, timedelta, timezone
from typing import Callable
from uuid import UUID

from src.domain.actuators.ports import ActuatorPort
from src.infrastructure.persistence.actuator_state_repository import (
    ActuatorStateRepository,
)


class PolicyBlockedError(RuntimeError):
    def __init__(
        self,
        message: str,
        policy_name: str,
    ):
        super().__init__(message)
        self.policy_name = policy_name


class MaxRuntimeActuatorDecorator(ActuatorPort):
    MAX_RUNTIME = timedelta(minutes=30)

    def __init__(
        self,
        inner: ActuatorPort,
        state_repository: ActuatorStateRepository,
        clock: Callable[[], datetime] | None = None,
    ):
        self.inner = inner
        self.state_repository = state_repository
        self.clock = clock or (
            lambda: datetime.now(timezone.utc)
        )

    def apply(
        self,
        device_id: UUID,
        command: str,
        payload: dict,
    ) -> None:
        state_row = self.state_repository.get_state(
            device_id
        )

        if (
            state_row is not None
            and state_row.state == "running"
        ):
            now = self.clock()

            elapsed = (
                now - state_row.updated_at
            )

            if elapsed >= self.MAX_RUNTIME:
                raise PolicyBlockedError(
                    message="Max run time exceeded",
                    policy_name="maxRunTime",
                )

        self.inner.apply(
            device_id=device_id,
            command=command,
            payload=payload,
        )