from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest
from sqlalchemy import select

from src.infrastructure.adapters.actuators.logging_decorator import (
    LoggingActuatorDecorator,
)
from src.infrastructure.adapters.actuators.max_runtime_decorator import (
    MaxRuntimeActuatorDecorator,
    PolicyBlockedError,
)
from src.infrastructure.db import SessionLocal
from src.infrastructure.persistence.execution_log_repository import (
    ExecutionLogRepository,
)
from src.infrastructure.persistence.models import (
    ActuatorExecutionLogRow,
    DeviceRow,
)


class FakeActuator:
    def __init__(self):
        self.calls = []

    def apply(
        self,
        device_id,
        command,
        payload,
    ):
        self.calls.append(
            {
                "device_id": device_id,
                "command": command,
                "payload": payload,
            }
        )


class FakeStateRepository:
    def __init__(self, state_row):
        self.state_row = state_row

    def get_state(self, device_id):
        return self.state_row


class FakeExecutionLogRepository:
    def __init__(self):
        self.rows = []

    def create(
        self,
        device_id,
        success,
        policy_applied,
        message=None,
    ):
        self.rows.append(
            {
                "device_id": device_id,
                "success": success,
                "policy_applied": policy_applied,
                "message": message,
            }
        )


def test_logging_decorator_records_success():
    device_id = uuid4()

    inner = FakeActuator()
    log_repository = (
        FakeExecutionLogRepository()
    )

    decorator = LoggingActuatorDecorator(
        inner=inner,
        execution_log_repository=(
            log_repository
        ),
    )

    decorator.apply(
        device_id=device_id,
        command="test_command",
        payload={},
    )

    assert len(inner.calls) == 1

    assert len(log_repository.rows) == 1

    row = log_repository.rows[0]

    assert row["success"] is True
    assert row["policy_applied"] == [
        "logging"
    ]
    assert row["message"] is None


def test_max_runtime_blocks_inner_adapter():
    device_id = uuid4()

    now = datetime.now(timezone.utc)

    state_row = SimpleNamespace(
        state="running",
        updated_at=(
            now - timedelta(minutes=31)
        ),
    )

    inner = FakeActuator()

    state_repository = (
        FakeStateRepository(state_row)
    )

    decorator = MaxRuntimeActuatorDecorator(
        inner=inner,
        state_repository=state_repository,
        clock=lambda: now,
    )

    with pytest.raises(
        PolicyBlockedError,
        match="Max run time exceeded",
    ):
        decorator.apply(
            device_id=device_id,
            command="test_command",
            payload={},
        )

    # The blocked request must not reach
    # the inner actuator adapter.
    assert inner.calls == []


def test_logging_records_blocked_policy():
    device_id = uuid4()

    now = datetime.now(timezone.utc)

    state_row = SimpleNamespace(
        state="running",
        updated_at=(
            now - timedelta(minutes=31)
        ),
    )

    inner = FakeActuator()

    state_repository = (
        FakeStateRepository(state_row)
    )

    log_repository = (
        FakeExecutionLogRepository()
    )

    max_runtime = (
        MaxRuntimeActuatorDecorator(
            inner=inner,
            state_repository=(
                state_repository
            ),
            clock=lambda: now,
        )
    )

    logging = LoggingActuatorDecorator(
        inner=max_runtime,
        execution_log_repository=(
            log_repository
        ),
    )

    with pytest.raises(
        PolicyBlockedError,
        match="Max run time exceeded",
    ):
        logging.apply(
            device_id=device_id,
            command="test_command",
            payload={},
        )

    assert inner.calls == []

    assert len(log_repository.rows) == 1

    row = log_repository.rows[0]

    assert row["success"] is False

    assert row["policy_applied"] == [
        "maxRunTime",
        "logging",
    ]

    assert (
        row["message"]
        == "Max run time exceeded"
    )


def test_logging_decorator_persists_execution():
    device_id = uuid4()
    log_id = None

    try:
        with SessionLocal() as db:
            device = DeviceRow(
                id=device_id,
                device_type="water_pump",
                role="actuator",
                device_family="simulation",
                display_name=(
                    "Phase 9 Test Pump"
                ),
                default_config={
                    "protocol": "simulation"
                },
                sampling_interval_seconds=300,
                tracking_enabled=False,
            )

            db.add(device)
            db.commit()

        with SessionLocal() as db:
            repository = (
                ExecutionLogRepository(db)
            )

            inner = FakeActuator()

            decorator = (
                LoggingActuatorDecorator(
                    inner=inner,
                    execution_log_repository=(
                        repository
                    ),
                )
            )

            decorator.apply(
                device_id=device_id,
                command="test_command",
                payload={},
            )

        with SessionLocal() as db:
            statement = (
                select(
                    ActuatorExecutionLogRow
                )
                .where(
                    ActuatorExecutionLogRow.device_id
                    == device_id
                )
                .order_by(
                    ActuatorExecutionLogRow.created_at.desc()
                )
            )

            stored = db.scalar(statement)

            assert stored is not None
            assert stored.success is True
            assert stored.policy_applied == [
                "logging"
            ]
            assert stored.message is None

            log_id = stored.id

    finally:
        with SessionLocal() as db:
            if log_id is not None:
                log_row = db.get(
                    ActuatorExecutionLogRow,
                    log_id,
                )

                if log_row is not None:
                    db.delete(log_row)
                    db.flush()

            device = db.get(
                DeviceRow,
                device_id,
            )

            if device is not None:
                db.delete(device)

            db.commit()