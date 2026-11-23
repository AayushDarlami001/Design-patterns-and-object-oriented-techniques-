from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar
from uuid import UUID


@dataclass(frozen=True)
class ReadingCreated:
    event_type: ClassVar[str] = "reading.created"

    device_id: UUID | None
    location_id: UUID | None
    zone_id: UUID | None

    value: float
    unit: str
    source: str
    recorded_at: datetime


@dataclass(frozen=True)
class ThresholdCrossed:
    event_type: ClassVar[str] = "threshold.crossed"

    device_id: UUID | None
    location_id: UUID | None
    zone_id: UUID | None

    value: float
    threshold_low: float


@dataclass(frozen=True)
class CommandFailed:
    event_type: ClassVar[str] = "command.failed"

    device_id: UUID | None
    location_id: UUID | None
    zone_id: UUID | None

    command_type: str
    error_message: str


@dataclass(frozen=True)
class ActuatorStateChanged:
    event_type: ClassVar[str] = "state.changed"

    device_id: UUID | None
    location_id: UUID | None
    zone_id: UUID | None

    previous_state: str
    state: str