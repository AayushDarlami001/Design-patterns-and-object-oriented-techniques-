from uuid import UUID

from src.domain.actuators.ports import ActuatorPort


class SimulationActuatorAdapter(ActuatorPort):
    def __init__(self):
        self.actions: list[dict] = []

    def apply(
        self,
        device_id: UUID,
        command: str,
        payload: dict,
    ) -> None:
        self.actions.append(
            {
                "device_id": device_id,
                "command": command,
                "payload": payload,
            }
        )