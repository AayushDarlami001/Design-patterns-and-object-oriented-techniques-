from datetime import datetime
from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from src.infrastructure.persistence.models import (
    AlertRow,
)


class AlertRepository:
    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def create(
        self,
        *,
        location_id: UUID | None,
        zone_id: UUID | None,
        device_id: UUID | None,
        severity: str,
        message: str,
        event_type: str,
        status: str = "active",
    ) -> AlertRow:
        row = AlertRow(
            location_id=location_id,
            zone_id=zone_id,
            device_id=device_id,
            severity=severity,
            message=message,
            event_type=event_type,
            status=status,
        )

        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)

        return row

    def list_alerts(
        self,
        *,
        status: str = "active",
        limit: int = 50,
        since: datetime | None = None,
        location_id: UUID | None = None,
        zone_id: UUID | None = None,
    ) -> list[AlertRow]:
        statement = select(AlertRow)

        if status != "all":
            statement = statement.where(
                AlertRow.status == status
            )

        if since is not None:
            statement = statement.where(
                AlertRow.created_at >= since
            )

        if location_id is not None:
            statement = statement.where(
                AlertRow.location_id
                == location_id
            )

        if zone_id is not None:
            statement = statement.where(
                AlertRow.zone_id == zone_id
            )

        statement = (
            statement
            .order_by(
                desc(AlertRow.created_at)
            )
            .limit(limit)
        )

        return list(
            self.db.scalars(
                statement
            ).all()
        )