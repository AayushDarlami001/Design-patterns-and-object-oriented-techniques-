from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.domain.sensors.reading import Reading
from src.infrastructure.persistence.models import ReadingRow


class ReadingRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(
        self,
        reading: Reading,
    ) -> Reading:
        row = ReadingRow(
            device_id=reading.device_id,
            value=reading.value,
            unit=reading.unit,
            source=reading.source,
            recorded_at=reading.recorded_at,
        )

        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)

        return Reading(
            device_id=row.device_id,
            value=float(row.value),
            unit=row.unit,
            source=row.source,
            recorded_at=row.recorded_at,
        )

    def list_recent(
        self,
        device_id: UUID,
        limit: int = 20,
    ) -> list[Reading]:
        statement = (
            select(ReadingRow)
            .where(
                ReadingRow.device_id == device_id
            )
            .order_by(
                ReadingRow.recorded_at.desc()
            )
            .limit(limit)
        )

        rows = self.session.scalars(
            statement
        ).all()

        return [
            Reading(
                device_id=row.device_id,
                value=float(row.value),
                unit=row.unit,
                source=row.source,
                recorded_at=row.recorded_at,
            )
            for row in rows
        ]

    def latest(
        self,
        device_id: UUID,
    ) -> Reading | None:
        readings = self.list_recent(
            device_id=device_id,
            limit=1,
        )

        if not readings:
            return None

        return readings[0]