from src.domain.locations.entity import (
    Location,
    LocationConfig,
    Zone,
)
from src.domain.locations.errors import ConfigurationError


def validate_zone_fields(
    name: str,
    moisture_threshold_low: float,
    moisture_threshold_high: float,
) -> None:
    if not name.strip():
        raise ConfigurationError("Zone name is required")

    if not 0.0 <= moisture_threshold_low <= 1.0:
        raise ConfigurationError(
            "Moisture low threshold must be between 0.0 and 1.0"
        )

    if not 0.0 <= moisture_threshold_high <= 1.0:
        raise ConfigurationError(
            "Moisture high threshold must be between 0.0 and 1.0"
        )

    if moisture_threshold_low >= moisture_threshold_high:
        raise ConfigurationError(
            "Moisture low threshold must be less than high threshold"
        )


class LocationConfigBuilder:
    def __init__(self):
        self._location_name: str | None = None
        self._zones: list[Zone] = []

    def set_location_name(
        self,
        name: str,
    ) -> "LocationConfigBuilder":
        self._location_name = name
        return self

    def add_zone(
        self,
        name: str,
        moisture_threshold_low: float,
        moisture_threshold_high: float,
        schedule: dict | None = None,
    ) -> "LocationConfigBuilder":
        self._zones.append(
            Zone(
                name=name,
                moisture_threshold_low=moisture_threshold_low,
                moisture_threshold_high=moisture_threshold_high,
                schedule=schedule or {},
            )
        )

        return self

    def build(self) -> LocationConfig:
        if self._location_name is None or not self._location_name.strip():
            raise ConfigurationError("Location name is required")

        if not self._zones:
            raise ConfigurationError(
                "At least one zone is required"
            )

        zone_names: set[str] = set()

        for zone in self._zones:
            validate_zone_fields(
                zone.name,
                zone.moisture_threshold_low,
                zone.moisture_threshold_high,
            )

            normalized_name = zone.name.strip().lower()

            if normalized_name in zone_names:
                raise ConfigurationError(
                    f"Duplicate zone name: {zone.name}"
                )

            zone_names.add(normalized_name)

        location = Location(
            name=self._location_name.strip(),
            zones=tuple(self._zones),
        )

        return LocationConfig(
            location=location,
        )