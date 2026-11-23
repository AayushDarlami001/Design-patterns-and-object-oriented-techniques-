from sqlalchemy.orm import Session

from src.application.alerts.setup import build_event_bus
from src.application.readings.service import ReadingIngest
from src.infrastructure.persistence.device_repository import (
    DeviceRepository,
)
from src.infrastructure.persistence.reading_repository import (
    ReadingRepository,
)


def build_reading_ingest(
    db: Session,
) -> ReadingIngest:
    return ReadingIngest(
        device_repository=DeviceRepository(db),
        reading_repository=ReadingRepository(db),
        event_bus=build_event_bus(db),
    )