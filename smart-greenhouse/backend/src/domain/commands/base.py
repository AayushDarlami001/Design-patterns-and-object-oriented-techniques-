from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ClassVar
from uuid import UUID

from src.domain.actuators.ports import ActuatorPort


@dataclass(frozen=True)
class CommandResult:
    status: str
    error_message: str | None = None


class Command(ABC):
    command_type: ClassVar[str]
    target_state: ClassVar[str | None] = None

    def __init__(
        self,
        device_id: UUID,
        payload: dict | None = None,
    ):
        self.device_id = device_id
        self.payload = payload or {}

    @abstractmethod
    def execute(
        self,
        port: ActuatorPort,
    ) -> None:
        pass