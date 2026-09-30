from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.sensors.reading import Reading


class SensorPort(ABC):
    @abstractmethod
    def read(
        self,
        device_id: UUID,
        device_type: str,
        config: dict,
    ) -> Reading:
        pass