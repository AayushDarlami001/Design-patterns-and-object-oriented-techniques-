import pytest

from src.domain.locations.config_builder import LocationConfigBuilder
from src.domain.locations.errors import ConfigurationError


def test_builder_success():
    config = (
        LocationConfigBuilder()
        .set_location_name("Main Greenhouse")
        .add_zone(
            "Zone A",
            0.30,
            0.70,
            {"start": "08:00", "end": "18:00"},
        )
        .build()
    )

    assert config.location.name == "Main Greenhouse"
    assert len(config.location.zones) == 1
    assert config.location.zones[0].name == "Zone A"


def test_builder_missing_location():
    builder = LocationConfigBuilder()

    builder.add_zone(
        "Zone A",
        0.30,
        0.70,
    )

    with pytest.raises(ConfigurationError):
        builder.build()


def test_builder_requires_zone():
    builder = LocationConfigBuilder()

    builder.set_location_name("Main Greenhouse")

    with pytest.raises(ConfigurationError):
        builder.build()


def test_builder_rejects_invalid_threshold_order():
    builder = LocationConfigBuilder()

    builder.set_location_name("Main Greenhouse")

    builder.add_zone(
        "Zone A",
        0.80,
        0.40,
    )

    with pytest.raises(ConfigurationError):
        builder.build()


def test_builder_rejects_threshold_outside_range():
    builder = LocationConfigBuilder()

    builder.set_location_name("Main Greenhouse")

    builder.add_zone(
        "Zone A",
        -0.10,
        0.70,
    )

    with pytest.raises(ConfigurationError):
        builder.build()


def test_builder_rejects_duplicate_zone_names():
    builder = LocationConfigBuilder()

    builder.set_location_name("Main Greenhouse")

    builder.add_zone(
        "Zone A",
        0.30,
        0.70,
    )

    builder.add_zone(
        "zone a",
        0.20,
        0.60,
    )

    with pytest.raises(ConfigurationError):
        builder.build()