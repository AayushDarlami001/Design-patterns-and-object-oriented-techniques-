from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from src.infrastructure.persistence.models import (
    ActuatorExecutionLogRow,
)


class ExecutionLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        device_id: UUID,
        success: bool,
        policy_applied: list[str],
        message: str | None = None,
    ) -> ActuatorExecutionLogRow:
        row = ActuatorExecutionLogRow(
            device_id=device_id,
            success=success,
            policy_applied=policy_applied,
            message=message,
        )

        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)

        return row

    def list_recent(
        self,
        limit: int = 20,
    ) -> list[ActuatorExecutionLogRow]:
        statement = (
            select(ActuatorExecutionLogRow)
            .order_by(
                desc(
                    ActuatorExecutionLogRow.created_at
                )
            )
            .limit(limit)
        )

        return list(
            self.db.scalars(statement).all()
        )