from uuid import uuid4

from sqlalchemy import select

from src.application.commands.dto import (
    CommandRequest,
)
from src.application.commands.service import (
    CommandService,
)
from src.infrastructure.db import SessionLocal
from src.infrastructure.persistence.models import (
    ActuatorStateRow,
    CommandLogRow,
    DeviceRow,
)


def test_successful_start_pump_updates_state_and_log():
    device_id = uuid4()

    try:
        with SessionLocal() as db:
            device = DeviceRow(
                id=device_id,
                device_type="water_pump",
                role="actuator",
                device_family="simulation",
                display_name="Phase 10 Test Pump",
                default_config={
                    "protocol": "simulation",
                },
                tracking_enabled=False,
                sampling_interval_seconds=300,
            )

            db.add(device)
            db.flush()

            state = ActuatorStateRow(
                device_id=device_id,
                state="idle",
            )

            db.add(state)
            db.commit()

        with SessionLocal() as db:
            service = CommandService(db)

            result = service.execute(
                CommandRequest(
                    command_type="start_pump",
                    device_id=device_id,
                    payload={},
                )
            )

            assert result.status == "success"
            assert result.command_type == "start_pump"
            assert result.error_message is None

        with SessionLocal() as db:
            stored_state = db.get(
                ActuatorStateRow,
                device_id,
            )

            assert stored_state is not None
            assert stored_state.state == "running"

            statement = (
                select(CommandLogRow)
                .where(
                    CommandLogRow.device_id
                    == device_id
                )
                .order_by(
                    CommandLogRow.created_at.desc()
                )
            )

            log = db.scalar(statement)

            assert log is not None
            assert log.command_type == "start_pump"
            assert log.status == "success"
            assert log.error_message is None

    finally:
        with SessionLocal() as db:
            device = db.get(
                DeviceRow,
                device_id,
            )

            if device is not None:
                db.delete(device)

            db.commit()


def test_rejected_command_does_not_change_state():
    device_id = uuid4()

    try:
        with SessionLocal() as db:
            device = DeviceRow(
                id=device_id,
                device_type="water_pump",
                role="actuator",
                device_family="simulation",
                display_name=(
                    "Phase 10 Rejected Test Pump"
                ),
                default_config={
                    "protocol": "simulation",
                },
                tracking_enabled=False,
                sampling_interval_seconds=300,
            )

            db.add(device)
            db.flush()

            state = ActuatorStateRow(
                device_id=device_id,
                state="idle",
            )

            db.add(state)
            db.commit()

        with SessionLocal() as db:
            service = CommandService(db)

            result = service.execute(
                CommandRequest(
                    command_type="stop_pump",
                    device_id=device_id,
                    payload={},
                )
            )

            assert result.status == "rejected"
            assert result.command_type == "stop_pump"
            assert result.error_message is not None

        with SessionLocal() as db:
            stored_state = db.get(
                ActuatorStateRow,
                device_id,
            )

            assert stored_state is not None

            # Rejected command must not
            # change Phase 8 state.
            assert stored_state.state == "idle"

            statement = (
                select(CommandLogRow)
                .where(
                    CommandLogRow.device_id
                    == device_id
                )
                .order_by(
                    CommandLogRow.created_at.desc()
                )
            )

            log = db.scalar(statement)

            assert log is not None
            assert log.command_type == "stop_pump"
            assert log.status == "rejected"
            assert log.error_message is not None

    finally:
        with SessionLocal() as db:
            device = db.get(
                DeviceRow,
                device_id,
            )

            if device is not None:
                db.delete(device)

            db.commit()