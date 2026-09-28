from uuid import UUID

from pydantic import BaseModel, Field


class ZoneCreateDto(BaseModel):
    name: str
    moisture_threshold_low: float
    moisture_threshold_high: float
    schedule: dict = Field(default_factory=dict)


class ZoneUpdateDto(BaseModel):
    name: str | None = None
    moisture_threshold_low: float | None = None
    moisture_threshold_high: float | None = None
    schedule: dict | None = None


class LocationConfigCreateRequest(BaseModel):
    location_name: str
    zones: list[ZoneCreateDto]


class LocationDto(BaseModel):
    id: UUID
    name: str


class ZoneDto(BaseModel):
    id: UUID
    location_id: UUID
    name: str
    moisture_threshold_low: float
    moisture_threshold_high: float
    schedule: dict


class LocationConfigResponse(BaseModel):
    location: LocationDto
    zones: list[ZoneDto]


class LocationListItemDto(BaseModel):
    id: UUID
    name: str


class DeviceZoneAssignmentRequest(BaseModel):
    zone_id: UUID | None = None