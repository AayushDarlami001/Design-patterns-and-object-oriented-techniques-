from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.domain.automation.context import (
    LocationAutomationContext,
)
from src.infrastructure.persistence.models import (
    AutomationRuleRow,
    DeviceRow,
    LocationRow,
    ReadingRow,
    ZoneRow,
)


class AutomationRepository:
    def __init__(self, db: Session):
        self.db = db

    def location_exists(
        self,
        location_id: UUID,
    ) -> bool:
        statement = select(
            LocationRow.id
        ).where(
            LocationRow.id == location_id
        )

        return (
            self.db.scalar(statement)
            is not None
        )

    def get_strategy_key(
        self,
        location_id: UUID,
    ) -> str | None:
        statement = select(
            AutomationRuleRow
        ).where(
            AutomationRuleRow.location_id
            == location_id
        )

        row = self.db.scalar(statement)

        if row is None:
            return None

        return row.strategy_key

    def upsert_strategy(
        self,
        location_id: UUID,
        strategy_key: str,
    ) -> str:
        statement = select(
            AutomationRuleRow
        ).where(
            AutomationRuleRow.location_id
            == location_id
        )

        row = self.db.scalar(statement)

        if row is None:
            row = AutomationRuleRow(
                location_id=location_id,
                strategy_key=strategy_key,
                parameters={},
            )

            self.db.add(row)

        else:
            row.strategy_key = strategy_key

        self.db.commit()
        self.db.refresh(row)

        return row.strategy_key

    def build_contexts(
        self,
        location_id: UUID,
    ) -> list[
        tuple[
            str,
            LocationAutomationContext,
        ]
    ]:
        zone_statement = (
            select(ZoneRow)
            .where(
                ZoneRow.location_id
                == location_id
            )
            .order_by(
                ZoneRow.created_at.asc()
            )
        )

        zones = list(
            self.db.scalars(
                zone_statement
            ).all()
        )

        contexts = []

        for zone in zones:
            moisture = (
                self._latest_sensor_value(
                    zone_id=zone.id,
                    device_type=(
                        "moisture_sensor"
                    ),
                )
            )

            light = (
                self._latest_sensor_value(
                    zone_id=zone.id,
                    device_type=(
                        "light_sensor"
                    ),
                )
            )

            context = (
                LocationAutomationContext(
                    location_id=location_id,
                    zone_id=zone.id,
                    moisture=moisture,
                    light=light,
                    moisture_threshold_low=float(
                        zone.moisture_threshold_low
                    ),
                    moisture_threshold_high=float(
                        zone.moisture_threshold_high
                    ),
                )
            )

            contexts.append(
                (
                    zone.name,
                    context,
                )
            )

        return contexts

    def _latest_sensor_value(
        self,
        zone_id: UUID,
        device_type: str,
    ) -> float | None:
        statement = (
            select(ReadingRow.value)
            .join(
                DeviceRow,
                ReadingRow.device_id
                == DeviceRow.id,
            )
            .where(
                DeviceRow.zone_id
                == zone_id,
                DeviceRow.role
                == "sensor",
                DeviceRow.device_type
                == device_type,
            )
            .order_by(
                ReadingRow.recorded_at.desc()
            )
            .limit(1)
        )

        value = self.db.scalar(
            statement
        )

        if value is None:
            return None

        return float(value)