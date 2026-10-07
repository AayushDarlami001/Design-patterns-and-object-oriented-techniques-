from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class LocationAutomationContext:
    location_id: UUID
    zone_id: UUID
    moisture: float | None
    moisture_threshold_low: float
    moisture_threshold_high: float
    light: float | None = None


@dataclass(frozen=True)
class Recommendation:
    action: str
    reason: str
    score: float | None = None