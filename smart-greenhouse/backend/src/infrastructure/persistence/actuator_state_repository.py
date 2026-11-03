from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.infrastructure.persistence.models import (
    ActuatorStateRow,
    DeviceRow,
)


class ActuatorStateRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_actuator(
        self,
        device_id: UUID,
    ) -> DeviceRow | None:
        statement = select(DeviceRow).where(
            DeviceRow.id == device_id,
            DeviceRow.role == "actuator",
        )

        return self.db.scalar(statement)

    def get_state(
        self,
        device_id: UUID,
    ) -> ActuatorStateRow | None:
        statement = select(
            ActuatorStateRow
        ).where(
            ActuatorStateRow.device_id
            == device_id
        )

        return self.db.scalar(statement)

    def save_state(
        self,
        device_id: UUID,
        state: str,
    ) -> ActuatorStateRow:
        state_row = self.get_state(
            device_id
        )

        if state_row is None:
            state_row = ActuatorStateRow(
                device_id=device_id,
                state=state,
            )

            self.db.add(state_row)
        else:
            state_row.state = state
            state_row.updated_at = (
                datetime.now(
                    timezone.utc
                )
            )

        self.db.commit()
        self.db.refresh(state_row)

        return state_row