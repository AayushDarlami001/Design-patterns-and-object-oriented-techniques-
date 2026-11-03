from uuid import uuid4

import pytest

from src.application.actuators.service import (
    ActuatorStateService,
)
from src.domain.actuators.state import (
    IllegalTransitionError,
)
from src.infrastructure.db import SessionLocal
from src.infrastructure.persistence.actuator_state_repository import (
    ActuatorStateRepository,
)
from src.infrastructure.persistence.models import (
    ActuatorStateRow,
    DeviceRow,
)


def test_legal_transition_updates_database():
    device_id = uuid4()

    try:
        with SessionLocal() as db:
            device = DeviceRow(
                id=device_id,
                device_type="water_pump",
                role="actuator",
                device_family="simulation",
                display_name="Phase 8 Test Pump",
                default_config={
                    "protocol": "simulation"
                },
                tracking_enabled=False,
                sampling_interval_seconds=300,
            )

            db.add(device)

            # Important:
            # persist the parent device first so
            # actuator_states FK can reference it.
            db.flush()

            state = ActuatorStateRow(
                device_id=device_id,
                state="idle",
            )

            db.add(state)
            db.commit()

        with SessionLocal() as db:
            repository = (
                ActuatorStateRepository(db)
            )

            service = ActuatorStateService(
                repository
            )

            result = service.transition(
                device_id=device_id,
                target_state="running",
            )

            assert result.state == "running"

        with SessionLocal() as db:
            stored = db.get(
                ActuatorStateRow,
                device_id,
            )

            assert stored is not None
            assert stored.state == "running"

    finally:
        with SessionLocal() as db:
            state = db.get(
                ActuatorStateRow,
                device_id,
            )

            if state is not None:
                db.delete(state)
                db.flush()

            device = db.get(
                DeviceRow,
                device_id,
            )

            if device is not None:
                db.delete(device)

            db.commit()


def test_illegal_transition_does_not_update_database():
    device_id = uuid4()

    try:
        with SessionLocal() as db:
            device = DeviceRow(
                id=device_id,
                device_type="water_pump",
                role="actuator",
                device_family="simulation",
                display_name=(
                    "Phase 8 Illegal Test Pump"
                ),
                default_config={
                    "protocol": "simulation"
                },
                tracking_enabled=False,
                sampling_interval_seconds=300,
            )

            db.add(device)

            # Parent device must exist before
            # actuator_states is inserted.
            db.flush()

            state = ActuatorStateRow(
                device_id=device_id,
                state="running",
            )

            db.add(state)
            db.commit()

        with SessionLocal() as db:
            repository = (
                ActuatorStateRepository(db)
            )

            service = ActuatorStateService(
                repository
            )

            with pytest.raises(
                IllegalTransitionError
            ):
                service.transition(
                    device_id=device_id,
                    target_state="maintenance",
                )

        with SessionLocal() as db:
            stored = db.get(
                ActuatorStateRow,
                device_id,
            )

            assert stored is not None

            # Illegal transition must not
            # change the database.
            assert stored.state == "running"

    finally:
        with SessionLocal() as db:
            state = db.get(
                ActuatorStateRow,
                device_id,
            )

            if state is not None:
                db.delete(state)
                db.flush()

            device = db.get(
                DeviceRow,
                device_id,
            )

            if device is not None:
                db.delete(device)

            db.commit()