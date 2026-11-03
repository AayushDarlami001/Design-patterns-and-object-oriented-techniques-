from uuid import UUID

from src.domain.actuators.context import (
    ActuatorContext,
)
from src.infrastructure.persistence.actuator_state_repository import (
    ActuatorStateRepository,
)


class ActuatorStateService:
    def __init__(
        self,
        repository: ActuatorStateRepository,
    ):
        self.repository = repository

    def get_context(
        self,
        device_id: UUID,
    ) -> ActuatorContext:
        actuator = self.repository.get_actuator(
            device_id
        )

        if actuator is None:
            raise LookupError(
                "Actuator not found"
            )

        state_row = self.repository.get_state(
            device_id
        )

        if state_row is None:
            state_row = self.repository.save_state(
                device_id=device_id,
                state="idle",
            )

        return ActuatorContext(
            device_id=device_id,
            state=state_row.state,
        )

    def get_state(
        self,
        device_id: UUID,
    ) -> ActuatorContext:
        return self.get_context(
            device_id
        )

    def transition(
        self,
        device_id: UUID,
        target_state: str,
    ) -> ActuatorContext:
        context = self.get_context(
            device_id
        )

        context.transition_to(
            target_state
        )
        self.repository.save_state(
            device_id=device_id,
            state=context.state,
        )

        return context