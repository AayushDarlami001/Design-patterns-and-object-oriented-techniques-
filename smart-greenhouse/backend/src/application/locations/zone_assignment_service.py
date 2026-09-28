from uuid import UUID

from src.domain.devices.entity import Device
from src.infrastructure.persistence.device_repository import (
    DeviceRepository,
)


class ZoneAssignmentService:
    def __init__(
        self,
        repository: DeviceRepository,
    ):
        self.repository = repository

    def assign(
        self,
        device_id: UUID,
        zone_id: UUID | None,
    ) -> Device | None:
        if zone_id is None:
            return self.repository.unassign_device(
                device_id
            )

        return self.repository.assign_device_to_zone(
            device_id,
            zone_id,
        )

    def list_zone_devices(
        self,
        location_id: UUID,
        zone_id: UUID,
    ) -> list[Device] | None:
        return self.repository.list_devices_in_zone(
            location_id,
            zone_id,
        )