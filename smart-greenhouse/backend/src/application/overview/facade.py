from collections import defaultdict
from uuid import UUID

from sqlalchemy.orm import Session

from src.application.automation.service import (
    AutomationService,
)
from src.application.overview.dto import (
    DeviceCountsDto,
    LocationOverviewDto,
    OverviewDeviceDto,
    OverviewLocationDto,
    OverviewReadingDto,
    OverviewZoneDto,
    RecommendationSummaryDto,
)
from src.infrastructure.persistence.automation_repository import (
    AutomationRepository,
)
from src.infrastructure.persistence.overview_repository import (
    OverviewRepository,
)


class LocationOverviewFacade:
    def __init__(
        self,
        db: Session,
    ):
        self.overview_repository = (
            OverviewRepository(db)
        )

        self.automation_repository = (
            AutomationRepository(db)
        )

        self.automation_service = (
            AutomationService(
                self.automation_repository
            )
        )

    def get_overview(
        self,
        location_id: UUID,
    ) -> LocationOverviewDto:
        location = (
            self.overview_repository
            .get_location(
                location_id
            )
        )

        if location is None:
            raise LookupError(
                "Location not found"
            )

        zones = (
            self.overview_repository
            .list_zones(
                location_id
            )
        )

        devices = (
            self.overview_repository
            .list_assigned_devices(
                location_id
            )
        )

        device_ids = [
            device.id
            for device in devices
        ]

        reading_rows = (
            self.overview_repository
            .list_latest_readings(
                device_ids
            )
        )

        latest_by_device = {
            row["device_id"]: row
            for row in reading_rows
        }

        devices_by_zone = defaultdict(
            list
        )

        for device in devices:
            if device.zone_id is not None:
                devices_by_zone[
                    device.zone_id
                ].append(device)

        sensor_count = sum(
            1
            for device in devices
            if device.role == "sensor"
        )

        actuator_count = sum(
            1
            for device in devices
            if device.role == "actuator"
        )

        zone_dtos = []

        for zone in zones:
            zone_devices = (
                devices_by_zone.get(
                    zone.id,
                    [],
                )
            )

            device_dtos = [
                OverviewDeviceDto(
                    id=device.id,
                    device_type=(
                        device.device_type
                    ),
                    role=device.role,
                    display_name=(
                        device.display_name
                    ),
                )
                for device
                in zone_devices
            ]

            reading_dtos = []

            for device in zone_devices:
                reading = (
                    latest_by_device.get(
                        device.id
                    )
                )

                if reading is None:
                    continue

                reading_dtos.append(
                    OverviewReadingDto(
                        device_id=(
                            device.id
                        ),
                        value=float(
                            reading[
                                "value"
                            ]
                        ),
                        unit=reading[
                            "unit"
                        ],
                        recorded_at=(
                            reading[
                                "recorded_at"
                            ]
                        ),
                        tracking_enabled=(
                            device
                            .tracking_enabled
                        ),
                        sampling_interval_seconds=(
                            device
                            .sampling_interval_seconds
                        ),
                    )
                )

            zone_dtos.append(
                OverviewZoneDto(
                    id=zone.id,
                    name=zone.name,
                    moisture_threshold_low=float(
                        zone
                        .moisture_threshold_low
                    ),
                    moisture_threshold_high=float(
                        zone
                        .moisture_threshold_high
                    ),
                    devices=device_dtos,
                    latest_readings=(
                        reading_dtos
                    ),
                )
            )

        strategy_key = (
            self.automation_repository
            .get_strategy_key(
                location_id
            )
        )

        last_recommendation = None

        if strategy_key is not None:
            evaluation = (
                self.automation_service
                .evaluate(
                    location_id
                )
            )

            last_recommendation = (
                RecommendationSummaryDto(
                    action=(
                        evaluation.action
                    ),
                    reason=(
                        evaluation.reason
                    ),
                )
            )

        return LocationOverviewDto(
            location=OverviewLocationDto(
                id=location.id,
                name=location.name,
            ),
            device_counts=(
                DeviceCountsDto(
                    sensor=sensor_count,
                    actuator=(
                        actuator_count
                    ),
                )
            ),
            zones=zone_dtos,
            strategy_key=strategy_key,
            last_recommendation=(
                last_recommendation
            ),
        )