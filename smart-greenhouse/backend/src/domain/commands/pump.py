from typing import ClassVar

from src.domain.actuators.ports import ActuatorPort
from src.domain.commands.base import Command


class StartPumpCommand(Command):
    command_type: ClassVar[str] = "start_pump"
    target_state: ClassVar[str | None] = "running"

    def execute(
        self,
        port: ActuatorPort,
    ) -> None:
        port.apply(
            device_id=self.device_id,
            command=self.command_type,
            payload=self.payload,
        )


class StopPumpCommand(Command):
    command_type: ClassVar[str] = "stop_pump"
    target_state: ClassVar[str | None] = "idle"

    def execute(
        self,
        port: ActuatorPort,
    ) -> None:
        port.apply(
            device_id=self.device_id,
            command=self.command_type,
            payload=self.payload,
        )