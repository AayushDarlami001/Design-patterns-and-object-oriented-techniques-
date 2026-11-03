from dataclasses import dataclass
from uuid import UUID

from src.domain.actuators.state import (
    get_allowed_commands,
    transition_state,
)


@dataclass
class ActuatorContext:
    device_id: UUID
    state: str

    @property
    def allowed_commands(self) -> list[str]:
        return get_allowed_commands(
            self.state
        )

    def transition_to(
        self,
        target_state: str,
    ) -> None:
        self.state = transition_state(
            current_state=self.state,
            target_state=target_state,
        )