from uuid import UUID

from src.application.locations.dto import (
    LocationConfigCreateRequest,
    LocationConfigResponse,
    LocationListItemDto,
    ZoneCreateDto,
    ZoneDto,
    ZoneUpdateDto,
)
from src.application.locations.mappers import (
    location_config_to_response,
    request_to_location_config,
)
from src.domain.locations.config_builder import (
    validate_zone_fields,
)
from src.domain.locations.entity import Zone
from src.domain.locations.errors import (
    ConfigurationError,
)
from src.infrastructure.persistence.location_repository import (
    LocationRepository,
)


class LocationConfigService:
    def __init__(
        self,
        repository: LocationRepository,
    ):
        self.repository = repository

    # -------------------------------------------------
    # Create configuration
    # -------------------------------------------------

    def create_config(
        self,
        request: LocationConfigCreateRequest,
    ) -> LocationConfigResponse:
        config = request_to_location_config(
            request
        )

        saved_config = self.repository.save_config(
            config
        )

        return location_config_to_response(
            saved_config
        )

    # -------------------------------------------------
    # Read configuration
    # -------------------------------------------------

    def get_config(
        self,
        location_id: UUID,
    ) -> LocationConfigResponse | None:
        config = self.repository.get_config(
            location_id
        )

        if config is None:
            return None

        return location_config_to_response(
            config
        )

    # -------------------------------------------------
    # List locations
    # -------------------------------------------------

    def list_locations(
        self,
    ) -> list[LocationListItemDto]:
        locations = self.repository.list_locations()

        return [
            LocationListItemDto(
                id=location.id,
                name=location.name,
            )
            for location in locations
            if location.id is not None
        ]

    # -------------------------------------------------
    # Delete location
    # -------------------------------------------------

    def delete_location(
        self,
        location_id: UUID,
    ) -> bool:
        return self.repository.delete_location(
            location_id
        )

    # -------------------------------------------------
    # Add zone
    # -------------------------------------------------

    def add_zone(
        self,
        location_id: UUID,
        request: ZoneCreateDto,
    ) -> ZoneDto | None:
        validate_zone_fields(
            request.name,
            request.moisture_threshold_low,
            request.moisture_threshold_high,
        )

        if self.repository.zone_name_exists(
            location_id,
            request.name,
        ):
            raise ConfigurationError(
                "Zone name must be unique within the location"
            )

        zone = Zone(
            name=request.name.strip(),
            moisture_threshold_low=(
                request.moisture_threshold_low
            ),
            moisture_threshold_high=(
                request.moisture_threshold_high
            ),
            schedule=request.schedule,
        )

        row = self.repository.add_zone(
            location_id,
            zone,
        )

        if row is None:
            return None

        return ZoneDto(
            id=row.id,
            location_id=row.location_id,
            name=row.name,
            moisture_threshold_low=float(
                row.moisture_threshold_low
            ),
            moisture_threshold_high=float(
                row.moisture_threshold_high
            ),
            schedule=row.schedule,
        )

    # -------------------------------------------------
    # Update zone
    # -------------------------------------------------

    def update_zone(
        self,
        location_id: UUID,
        zone_id: UUID,
        request: ZoneUpdateDto,
    ) -> ZoneDto | None:
        row = self.repository.get_zone(
            location_id,
            zone_id,
        )

        if row is None:
            return None

        name = (
            request.name
            if request.name is not None
            else row.name
        )

        low = (
            request.moisture_threshold_low
            if request.moisture_threshold_low is not None
            else float(row.moisture_threshold_low)
        )

        high = (
            request.moisture_threshold_high
            if request.moisture_threshold_high is not None
            else float(row.moisture_threshold_high)
        )

        schedule = (
            request.schedule
            if request.schedule is not None
            else row.schedule
        )

        validate_zone_fields(
            name,
            low,
            high,
        )

        if self.repository.zone_name_exists(
            location_id,
            name,
            exclude_zone_id=zone_id,
        ):
            raise ConfigurationError(
                "Zone name must be unique within the location"
            )

        updated = self.repository.update_zone(
            row=row,
            name=name.strip(),
            moisture_threshold_low=low,
            moisture_threshold_high=high,
            schedule=schedule,
        )

        return ZoneDto(
            id=updated.id,
            location_id=updated.location_id,
            name=updated.name,
            moisture_threshold_low=float(
                updated.moisture_threshold_low
            ),
            moisture_threshold_high=float(
                updated.moisture_threshold_high
            ),
            schedule=updated.schedule,
        )

    # -------------------------------------------------
    # Delete zone
    # -------------------------------------------------

    def delete_zone(
        self,
        location_id: UUID,
        zone_id: UUID,
    ) -> bool:
        zone = self.repository.get_zone(
            location_id,
            zone_id,
        )

        if zone is None:
            return False

        zone_count = self.repository.count_zones(
            location_id
        )

        if zone_count <= 1:
            raise ConfigurationError(
                "Cannot delete the last zone of a location"
            )

        return self.repository.delete_zone(
            location_id,
            zone_id,
        )