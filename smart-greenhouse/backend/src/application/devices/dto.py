from uuid import UUID

from pydantic import BaseModel, Field


class DeviceDto(BaseModel):
    id: UUID
    device_type: str
    role: str
    device_family: str
    display_name: str
    default_config: dict
    zone_id: UUID | None = None
    location_id: UUID | None = None
    sampling_interval_seconds: int = 300
    tracking_enabled: bool = True

    # Phase 8 — State
    state: str | None = None

    allowed_commands: list[str] = Field(
        default_factory=list
    )


class DeviceSamplingUpdateRequest(BaseModel):
    sampling_interval_seconds: int
    tracking_enabled: bool