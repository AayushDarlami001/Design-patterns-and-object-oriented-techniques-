import uuid
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Zone:
    name: str
    moisture_threshold_low: float
    moisture_threshold_high: float
    schedule: dict = field(default_factory=dict)
    id: uuid.UUID | None = None


@dataclass(frozen=True)
class Location:
    name: str
    zones: tuple[Zone, ...]
    id: uuid.UUID | None = None


@dataclass(frozen=True)
class LocationConfig:
    location: Location