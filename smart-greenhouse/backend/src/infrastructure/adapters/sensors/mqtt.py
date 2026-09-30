from datetime import datetime, timezone
from uuid import UUID

from src.domain.sensors.ports import SensorPort
from src.domain.sensors.reading import Reading


class MqttSensorAdapter(SensorPort):
    def __init__(self, payload: dict):
        self.payload = payload

    def read(
        self,
        device_id: UUID,
        device_type: str,
        config: dict,
    ) -> Reading:
        if "value" not in self.payload:
            raise ValueError(
                "MQTT payload is missing value"
            )

        if "unit" not in self.payload:
            raise ValueError(
                "MQTT payload is missing unit"
            )

        return Reading(
            device_id=device_id,
            value=float(
                self.payload["value"]
            ),
            unit=str(
                self.payload["unit"]
            ),
            source="mqtt",
            recorded_at=datetime.now(timezone.utc),
        )