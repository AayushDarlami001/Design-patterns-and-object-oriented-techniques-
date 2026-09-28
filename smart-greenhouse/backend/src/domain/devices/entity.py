import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class Device:
    id: uuid.UUID | None
    device_type: str
    role: str
    device_family: str
    display_name: str
    default_config: dict
    zone_id: uuid.UUID | None = None
    location_id: uuid.UUID | None = None