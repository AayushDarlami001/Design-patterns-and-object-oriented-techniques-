from typing import ClassVar

from src.domain.actuators.ports import ActuatorPort
from src.domain.commands.base import Command


class SetLightLevelCommand(Command):
    command_type: ClassVar[str] = "set_light_level"

    # Changing the light level does not change
    # the actuator lifecycle state.
    target_state: ClassVar[str | None] = None

    def execute(
        self,
        port: ActuatorPort,
    ) -> None:
        port.apply(
            device_id=self.device_id,
            command=self.command_type,
            payload=self.payload,
        )