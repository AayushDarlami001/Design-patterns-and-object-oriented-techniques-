from src.application.locations.dto import (
    LocationConfigCreateRequest,
    LocationConfigResponse,
    LocationDto,
    ZoneDto,
)
from src.domain.locations.config_builder import LocationConfigBuilder
from src.domain.locations.entity import LocationConfig


def request_to_location_config(
    request: LocationConfigCreateRequest,
) -> LocationConfig:
    builder = LocationConfigBuilder()

    builder.set_location_name(request.location_name)

    for zone in request.zones:
        builder.add_zone(
            name=zone.name,
            moisture_threshold_low=zone.moisture_threshold_low,
            moisture_threshold_high=zone.moisture_threshold_high,
            schedule=zone.schedule,
        )

    return builder.build()


def location_config_to_response(
    config: LocationConfig,
) -> LocationConfigResponse:
    location = config.location

    if location.id is None:
        raise ValueError(
            "Location must be saved before creating response"
        )

    return LocationConfigResponse(
        location=LocationDto(
            id=location.id,
            name=location.name,
        ),
        zones=[
            ZoneDto(
                id=zone.id,
                location_id=location.id,
                name=zone.name,
                moisture_threshold_low=zone.moisture_threshold_low,
                moisture_threshold_high=zone.moisture_threshold_high,
                schedule=zone.schedule,
            )
            for zone in location.zones
            if zone.id is not None
        ],
    )