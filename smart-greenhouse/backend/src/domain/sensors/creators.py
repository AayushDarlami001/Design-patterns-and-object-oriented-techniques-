from abc import ABC, abstractmethod

from src.domain.sensors.entity import Sensor


class SensorCreator(ABC):

    @abstractmethod
    def create_sensor(self, display_name: str | None = None) -> Sensor:
        pass


class MoistureSensorCreator(SensorCreator):

    def create_sensor(self, display_name: str | None = None) -> Sensor:
        return Sensor(
            id=None,
            device_type="moisture_sensor",
            display_name=display_name or "Moisture Sensor",
            default_config={
                "unit": "%",
                "sampling_interval": 5,
                "moisture_threshold": 30,
            },
        )


class LightSensorCreator(SensorCreator):

    def create_sensor(self, display_name: str | None = None) -> Sensor:
        return Sensor(
            id=None,
            device_type="light_sensor",
            display_name=display_name or "Light Sensor",
            default_config={
                "unit": "lux",
                "sampling_interval": 5,
            },
        )


SENSOR_CREATORS: dict[str, SensorCreator] = {
    "moisture": MoistureSensorCreator(),
    "light": LightSensorCreator(),
}


def get_sensor_creator(sensor_type: str) -> SensorCreator:
    creator = SENSOR_CREATORS.get(sensor_type)

    if creator is None:
        raise ValueError(f"Unknown sensor type: {sensor_type}")

    return creator