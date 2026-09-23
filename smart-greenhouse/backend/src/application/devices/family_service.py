from src.domain.devices.entity import Device
from src.domain.devices.family_factory import get_device_family_factory
from src.infrastructure.persistence.device_repository import DeviceRepository


class DeviceFamilyService:
    def __init__(self, repository: DeviceRepository):
        self.repository = repository

    def provision_family(self, family: str) -> list[Device]:
        factory = get_device_family_factory(family)

        devices = factory.create_device_set()

        return self.repository.save_devices(devices)

    def list_devices(
        self,
        family: str | None = None,
        role: str | None = None,
    ) -> list[Device]:
        return self.repository.list_devices(
            device_family=family,
            role=role,
        )