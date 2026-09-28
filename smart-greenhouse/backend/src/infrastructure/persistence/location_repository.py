from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.domain.locations.entity import (
    Location,
    LocationConfig,
    Zone,
)
from src.infrastructure.persistence.models import (
    DeviceRow,
    LocationRow,
    ZoneRow,
)


class LocationRepository:
    def __init__(self, session: Session):
        self.session = session

    # -------------------------------------------------
    # Create complete location configuration
    # -------------------------------------------------

    def save_config(
        self,
        config: LocationConfig,
    ) -> LocationConfig:
        try:
            location_row = LocationRow(
                name=config.location.name,
            )

            self.session.add(location_row)
            self.session.flush()

            zone_rows: list[ZoneRow] = []

            for zone in config.location.zones:
                row = ZoneRow(
                    location_id=location_row.id,
                    name=zone.name,
                    moisture_threshold_low=zone.moisture_threshold_low,
                    moisture_threshold_high=zone.moisture_threshold_high,
                    schedule=zone.schedule,
                )

                zone_rows.append(row)

            self.session.add_all(zone_rows)
            self.session.flush()

            self.session.commit()

            saved_zones = tuple(
                Zone(
                    id=row.id,
                    name=row.name,
                    moisture_threshold_low=float(
                        row.moisture_threshold_low
                    ),
                    moisture_threshold_high=float(
                        row.moisture_threshold_high
                    ),
                    schedule=row.schedule,
                )
                for row in zone_rows
            )

            saved_location = Location(
                id=location_row.id,
                name=location_row.name,
                zones=saved_zones,
            )

            return LocationConfig(
                location=saved_location,
            )

        except Exception:
            self.session.rollback()
            raise

    # -------------------------------------------------
    # Read one location configuration
    # -------------------------------------------------

    def get_config(
        self,
        location_id: UUID,
    ) -> LocationConfig | None:
        location_row = self.session.get(
            LocationRow,
            location_id,
        )

        if location_row is None:
            return None

        statement = (
            select(ZoneRow)
            .where(
                ZoneRow.location_id == location_id
            )
            .order_by(ZoneRow.name)
        )

        zone_rows = self.session.scalars(
            statement
        ).all()

        zones = tuple(
            Zone(
                id=row.id,
                name=row.name,
                moisture_threshold_low=float(
                    row.moisture_threshold_low
                ),
                moisture_threshold_high=float(
                    row.moisture_threshold_high
                ),
                schedule=row.schedule,
            )
            for row in zone_rows
        )

        location = Location(
            id=location_row.id,
            name=location_row.name,
            zones=zones,
        )

        return LocationConfig(
            location=location,
        )

    # -------------------------------------------------
    # List locations
    # -------------------------------------------------

    def list_locations(self) -> list[Location]:
        statement = (
            select(LocationRow)
            .order_by(LocationRow.created_at.desc())
        )

        rows = self.session.scalars(
            statement
        ).all()

        return [
            Location(
                id=row.id,
                name=row.name,
                zones=(),
            )
            for row in rows
        ]

    # -------------------------------------------------
    # Delete location
    # -------------------------------------------------

    def delete_location(
        self,
        location_id: UUID,
    ) -> bool:
        row = self.session.get(
            LocationRow,
            location_id,
        )

        if row is None:
            return False

        try:
            # Clear both assignment fields first.
            statement = select(DeviceRow).where(
                DeviceRow.location_id == location_id
            )

            devices = self.session.scalars(
                statement
            ).all()

            for device in devices:
                device.zone_id = None
                device.location_id = None

            self.session.delete(row)
            self.session.commit()

            return True

        except Exception:
            self.session.rollback()
            raise

    # -------------------------------------------------
    # Zone helpers
    # -------------------------------------------------

    def get_zone(
        self,
        location_id: UUID,
        zone_id: UUID,
    ) -> ZoneRow | None:
        statement = select(ZoneRow).where(
            ZoneRow.id == zone_id,
            ZoneRow.location_id == location_id,
        )

        return self.session.scalar(statement)

    def zone_name_exists(
        self,
        location_id: UUID,
        name: str,
        exclude_zone_id: UUID | None = None,
    ) -> bool:
        statement = select(ZoneRow).where(
            ZoneRow.location_id == location_id,
            func.lower(ZoneRow.name) == name.strip().lower(),
        )

        if exclude_zone_id is not None:
            statement = statement.where(
                ZoneRow.id != exclude_zone_id
            )

        return self.session.scalar(statement) is not None

    def count_zones(
        self,
        location_id: UUID,
    ) -> int:
        statement = (
            select(func.count())
            .select_from(ZoneRow)
            .where(
                ZoneRow.location_id == location_id
            )
        )

        return int(
            self.session.scalar(statement) or 0
        )

    # -------------------------------------------------
    # Add zone
    # -------------------------------------------------

    def add_zone(
        self,
        location_id: UUID,
        zone: Zone,
    ) -> ZoneRow | None:
        location = self.session.get(
            LocationRow,
            location_id,
        )

        if location is None:
            return None

        row = ZoneRow(
            location_id=location_id,
            name=zone.name,
            moisture_threshold_low=zone.moisture_threshold_low,
            moisture_threshold_high=zone.moisture_threshold_high,
            schedule=zone.schedule,
        )

        try:
            self.session.add(row)
            self.session.commit()
            self.session.refresh(row)

            return row

        except Exception:
            self.session.rollback()
            raise

    # -------------------------------------------------
    # Update zone
    # -------------------------------------------------

    def update_zone(
        self,
        row: ZoneRow,
        name: str,
        moisture_threshold_low: float,
        moisture_threshold_high: float,
        schedule: dict,
    ) -> ZoneRow:
        try:
            row.name = name
            row.moisture_threshold_low = (
                moisture_threshold_low
            )
            row.moisture_threshold_high = (
                moisture_threshold_high
            )
            row.schedule = schedule

            self.session.commit()
            self.session.refresh(row)

            return row

        except Exception:
            self.session.rollback()
            raise

    # -------------------------------------------------
    # Delete zone
    # -------------------------------------------------

    def delete_zone(
        self,
        location_id: UUID,
        zone_id: UUID,
    ) -> bool:
        zone = self.get_zone(
            location_id,
            zone_id,
        )

        if zone is None:
            return False

        try:
            # Clear BOTH assignment fields before deleting zone.
            statement = select(DeviceRow).where(
                DeviceRow.zone_id == zone_id
            )

            devices = self.session.scalars(
                statement
            ).all()

            for device in devices:
                device.zone_id = None
                device.location_id = None

            self.session.delete(zone)
            self.session.commit()

            return True

        except Exception:
            self.session.rollback()
            raise