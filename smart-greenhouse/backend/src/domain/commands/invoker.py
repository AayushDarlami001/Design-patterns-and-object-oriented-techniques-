from collections.abc import Mapping
from typing import Type
from uuid import UUID

from src.domain.actuators.ports import ActuatorPort
from src.domain.commands.base import Command
from src.domain.commands.light import (
    SetLightLevelCommand,
)
from src.domain.commands.pump import (
    StartPumpCommand,
    StopPumpCommand,
)


class UnknownCommandError(ValueError):
    pass


COMMAND_REGISTRY: dict[
    str,
    Type[Command],
] = {
    StartPumpCommand.command_type:
        StartPumpCommand,

    StopPumpCommand.command_type:
        StopPumpCommand,

    SetLightLevelCommand.command_type:
        SetLightLevelCommand,
}


class CommandInvoker:
    def __init__(
        self,
        registry: Mapping[
            str,
            Type[Command],
        ] | None = None,
    ):
        self.registry = dict(
            registry or COMMAND_REGISTRY
        )

    def create(
        self,
        command_type: str,
        device_id: UUID,
        payload: dict | None = None,
    ) -> Command:
        command_class = self.registry.get(
            command_type
        )

        if command_class is None:
            raise UnknownCommandError(
                "Unknown command type: "
                f"{command_type}"
            )

        return command_class(
            device_id=device_id,
            payload=payload,
        )

    def execute(
        self,
        command: Command,
        port: ActuatorPort,
    ) -> Command:
        command.execute(port)

        return command