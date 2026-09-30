import random
from datetime import datetime, timezone
from uuid import UUID

from src.domain.sensors.ports import SensorPort
from src.domain.sensors.reading import Reading


class SimulationSensorAdapter(SensorPort):
    def read(
        self,
        device_id: UUID,
        device_type: str,
        config: dict,
    ) -> Reading:
        if "moisture" in device_type:
            value = random.uniform(0.2, 0.6)
            unit = "vwc"

        elif "light" in device_type:
            value = random.uniform(200, 2000)
            unit = "lux"

        else:
            raise ValueError(
                f"Unsupported simulation sensor: {device_type}"
            )

        return Reading(
            device_id=device_id,
            value=round(value, 4),
            unit=unit,
            source="simulation",
            recorded_at=datetime.now(timezone.utc),
        )