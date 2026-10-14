from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.infrastructure.persistence.models import (
    DeviceRow,
    LocationRow,
    ReadingRow,
    ZoneRow,
)


class OverviewRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_location(
        self,
        location_id: UUID,
    ) -> LocationRow | None:
        statement = select(
            LocationRow
        ).where(
            LocationRow.id == location_id
        )

        return self.db.scalar(statement)

    def list_zones(
        self,
        location_id: UUID,
    ) -> list[ZoneRow]:
        statement = (
            select(ZoneRow)
            .where(
                ZoneRow.location_id
                == location_id
            )
            .order_by(
                ZoneRow.created_at.asc()
            )
        )

        return list(
            self.db.scalars(
                statement
            ).all()
        )

    def list_assigned_devices(
        self,
        location_id: UUID,
    ) -> list[DeviceRow]:
        statement = (
            select(DeviceRow)
            .where(
                DeviceRow.location_id
                == location_id,
                DeviceRow.zone_id.is_not(
                    None
                ),
            )
            .order_by(
                DeviceRow.created_at.asc()
            )
        )

        return list(
            self.db.scalars(
                statement
            ).all()
        )

    def list_latest_readings(
        self,
        device_ids: list[UUID],
    ):
        if not device_ids:
            return []

        ranked = (
            select(
                ReadingRow.device_id.label(
                    "device_id"
                ),
                ReadingRow.value.label(
                    "value"
                ),
                ReadingRow.unit.label(
                    "unit"
                ),
                ReadingRow.recorded_at.label(
                    "recorded_at"
                ),
                func.row_number()
                .over(
                    partition_by=(
                        ReadingRow.device_id
                    ),
                    order_by=(
                        ReadingRow.recorded_at.desc()
                    ),
                )
                .label("row_number"),
            )
            .where(
                ReadingRow.device_id.in_(
                    device_ids
                )
            )
            .subquery()
        )

        statement = (
            select(
                ranked.c.device_id,
                ranked.c.value,
                ranked.c.unit,
                ranked.c.recorded_at,
            )
            .where(
                ranked.c.row_number == 1
            )
        )

        return list(
            self.db.execute(
                statement
            ).mappings().all()
        )