from datetime import datetime

from src.application.readings.dto import ReadingDto
from src.application.readings.service import ReadingIngest
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


class SimulationSampler:
    def __init__(
        self,
        device_repository: DeviceRepository,
        reading_repository: ReadingRepository,
        ingest: ReadingIngest,
    ):
        self.device_repository = device_repository
        self.reading_repository = reading_repository
        self.ingest = ingest

    def run_once(
        self,
        now: datetime,
    ) -> list[ReadingDto]:
        if now.tzinfo is None:
            raise ValueError(
                "Sampler time must be timezone-aware"
            )

        recorded: list[ReadingDto] = []

        devices = (
            self.device_repository
            .list_tracked_simulation_sensors()
        )

        for device in devices:
            if device.id is None:
                continue

            latest = self.reading_repository.latest(
                device.id
            )

            if latest is not None:
                elapsed = (
                    now - latest.recorded_at
                ).total_seconds()

                if (
                    elapsed
                    < device.sampling_interval_seconds
                ):
                    continue

            adapter = select_sensor_adapter(
                device.default_config
            )

            generated = adapter.read(
                device_id=device.id,
                device_type=device.device_type,
                config=device.default_config,
            )

            reading = Reading(
                device_id=device.id,
                value=generated.value,
                unit=generated.unit,
                source=generated.source,
                recorded_at=now,
            )

            saved = self.ingest.record(
                device_id=device.id,
                translated_reading=reading,
            )

            recorded.append(saved)

        return recorded