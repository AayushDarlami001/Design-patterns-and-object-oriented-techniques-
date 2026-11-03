from src.application.actuators.service import (
    ActuatorStateService,
)
from src.application.devices.dto import DeviceDto
from src.application.devices.mappers import (
    device_to_dto,
)
from src.infrastructure.persistence.device_repository import (
    DeviceRepository,
)


class DeviceReadService:
    def __init__(
        self,
        device_repository: DeviceRepository,
        actuator_state_service: ActuatorStateService,
    ):
        self.device_repository = device_repository
        self.actuator_state_service = (
            actuator_state_service
        )

    def list_devices(
        self,
        family: str | None = None,
        role: str | None = None,
    ) -> list[DeviceDto]:
        devices = (
            self.device_repository.list_devices(
                device_family=family,
                role=role,
            )
        )

        result: list[DeviceDto] = []

        for device in devices:
            if device.role == "actuator":
                context = (
                    self.actuator_state_service
                    .get_state(device.id)
                )

                result.append(
                    device_to_dto(
                        device,
                        state=context.state,
                        allowed_commands=(
                            context.allowed_commands
                        ),
                    )
                )

            else:
                result.append(
                    device_to_dto(device)
                )

        return result