from datetime import datetime, timezone
from uuid import UUID

from src.domain.sensors.ports import SensorPort
from src.domain.sensors.reading import Reading


class VendorStubSensorAdapter(SensorPort):
    def __init__(self, raw_payload: dict):
        self.raw_payload = raw_payload

    def read(
        self,
        device_id: UUID,
        device_type: str,
        config: dict,
    ) -> Reading:
        if "reading_value" not in self.raw_payload:
            raise ValueError(
                "Vendor payload is missing reading_value"
            )

        if "reading_unit" not in self.raw_payload:
            raise ValueError(
                "Vendor payload is missing reading_unit"
            )

        return Reading(
            device_id=device_id,
            value=float(
                self.raw_payload["reading_value"]
            ),
            unit=str(
                self.raw_payload["reading_unit"]
            ),
            source="vendor",
            recorded_at=datetime.now(timezone.utc),
        )