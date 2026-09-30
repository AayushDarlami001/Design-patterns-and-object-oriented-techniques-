from uuid import UUID

from src.application.readings.dto import ReadingDto
from src.domain.sensors.reading import Reading
from src.infrastructure.adapters.sensors.selector import (
    select_sensor_adapter,
)
from src.infrastructure.persistence.device_repository import (
    DeviceRepository,
)
from src.infrastructure.persistence.reading_repository import (
    ReadingRepository,
)


class ReadingIngest:
    def __init__(
        self,
        device_repository: DeviceRepository,
        reading_repository: ReadingRepository,
    ):
        self.device_repository = device_repository
        self.reading_repository = reading_repository

    def record(
        self,
        device_id: UUID,
        translated_reading: Reading | None = None,
    ) -> ReadingDto:
        device = self.device_repository.get_device(
            device_id
        )

        if device is None:
            raise LookupError(
                "Device not found"
            )

        if device.role != "sensor":
            raise ValueError(
                "Device is not a sensor"
            )

        if translated_reading is None:
            adapter = select_sensor_adapter(
                device.default_config
            )

            reading = adapter.read(
                device_id=device_id,
                device_type=device.device_type,
                config=device.default_config,
            )

        else:
            if (
                translated_reading.device_id
                != device_id
            ):
                raise ValueError(
                    "Reading device id does not match"
                )

            reading = translated_reading

        saved = self.reading_repository.add(
            reading
        )

        return self._to_dto(saved)

    def list_recent(
        self,
        device_id: UUID,
        limit: int = 20,
    ) -> list[ReadingDto]:
        device = self.device_repository.get_device(
            device_id
        )

        if device is None:
            raise LookupError(
                "Device not found"
            )

        readings = self.reading_repository.list_recent(
            device_id=device_id,
            limit=limit,
        )

        return [
            self._to_dto(reading)
            for reading in readings
        ]

    @staticmethod
    def _to_dto(
        reading: Reading,
    ) -> ReadingDto:
        return ReadingDto(
            device_id=reading.device_id,
            value=reading.value,
            unit=reading.unit,
            source=reading.source,
            recorded_at=reading.recorded_at,
        )