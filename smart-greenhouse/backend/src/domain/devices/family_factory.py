from abc import ABC, abstractmethod

from src.domain.devices.entity import Device
from src.domain.sensors.creators import get_sensor_creator


class DeviceFamilyFactory(ABC):
    family_key: str

    @abstractmethod
    def create_device_set(self) -> list[Device]:
        pass


class SimulationDeviceFactory(DeviceFamilyFactory):
    family_key = "simulation"

    def create_device_set(self) -> list[Device]:
        moisture = get_sensor_creator("moisture").create_sensor(
            "Simulation Moisture Sensor"
        )

        light = get_sensor_creator("light").create_sensor(
            "Simulation Light Sensor"
        )

        return [
            Device(
                id=None,
                device_type=moisture.device_type,
                role="sensor",
                device_family=self.family_key,
                display_name=moisture.display_name,
                default_config={
                    **moisture.default_config,
                    "protocol": "simulation",
                },
            ),
            Device(
                id=None,
                device_type=light.device_type,
                role="sensor",
                device_family=self.family_key,
                display_name=light.display_name,
                default_config={
                    **light.default_config,
                    "protocol": "simulation",
                },
            ),
            Device(
                id=None,
                device_type="water_pump",
                role="actuator",
                device_family=self.family_key,
                display_name="Simulation Water Pump",
                default_config={
                    "protocol": "simulation",
                    "state": "off",
                },
            ),
            Device(
                id=None,
                device_type="grow_light",
                role="actuator",
                device_family=self.family_key,
                display_name="Simulation Grow Light",
                default_config={
                    "protocol": "simulation",
                    "state": "off",
                },
            ),
        ]


class EdgeDeviceFactory(DeviceFamilyFactory):
    family_key = "edge"

    def create_device_set(self) -> list[Device]:
        moisture = get_sensor_creator("moisture").create_sensor(
            "Edge Moisture Sensor"
        )

        light = get_sensor_creator("light").create_sensor(
            "Edge Light Sensor"
        )

        return [
            Device(
                id=None,
                device_type=moisture.device_type,
                role="sensor",
                device_family=self.family_key,
                display_name=moisture.display_name,
                default_config={
                    **moisture.default_config,
                    "protocol": "gpio",
                },
            ),
            Device(
                id=None,
                device_type=light.device_type,
                role="sensor",
                device_family=self.family_key,
                display_name=light.display_name,
                default_config={
                    **light.default_config,
                    "protocol": "i2c",
                },
            ),
            Device(
                id=None,
                device_type="water_pump",
                role="actuator",
                device_family=self.family_key,
                display_name="Edge Water Pump",
                default_config={
                    "protocol": "gpio",
                    "pin": 17,
                    "state": "off",
                },
            ),
            Device(
                id=None,
                device_type="grow_light",
                role="actuator",
                device_family=self.family_key,
                display_name="Edge Grow Light",
                default_config={
                    "protocol": "gpio",
                    "pin": 18,
                    "state": "off",
                },
            ),
        ]


DEVICE_FAMILY_FACTORIES: dict[str, DeviceFamilyFactory] = {
    "simulation": SimulationDeviceFactory(),
    "edge": EdgeDeviceFactory(),
}


def get_device_family_factory(family: str) -> DeviceFamilyFactory:
    factory = DEVICE_FAMILY_FACTORIES.get(family)

    if factory is None:
        raise ValueError(f"Unknown device family: {family}")

    return factory