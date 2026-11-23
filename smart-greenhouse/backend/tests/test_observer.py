from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from src.application.alerts.setup import (
    build_event_bus,
)
from src.application.commands.dto import (
    CommandRequest,
)
from src.application.commands.service import (
    CommandService,
)
from src.application.readings.service import (
    ReadingIngest,
)
from src.domain.events.bus import EventBus
from src.domain.events.events import (
    CommandFailed,
    ReadingCreated,
)
from src.domain.sensors.reading import Reading
from src.infrastructure.db import SessionLocal
from src.infrastructure.persistence.device_repository import (
    DeviceRepository,
)
from src.infrastructure.persistence.models import (
    ActuatorStateRow,
    AlertRow,
    CommandLogRow,
    DeviceRow,
    ReadingRow,
)
from src.infrastructure.persistence.reading_repository import (
    ReadingRepository,
)
from src.main import app


client = TestClient(app)


def test_subscriber_inserts_alert_on_published_event():
    message = (
        f"Phase 11 subscriber test {uuid4()}"
    )

    try:
        with SessionLocal() as db:
            event_bus = build_event_bus(db)

            event_bus.publish(
                CommandFailed(
                    device_id=None,
                    location_id=None,
                    zone_id=None,
                    command_type="test_command",
                    error_message=message,
                )
            )

        with SessionLocal() as db:
            statement = select(
                AlertRow
            ).where(
                AlertRow.message == message
            )

            alert = db.scalar(statement)

            assert alert is not None
            assert alert.severity == "warning"
            assert alert.event_type == "command.failed"
            assert alert.status == "active"

    finally:
        with SessionLocal() as db:
            db.execute(
                delete(AlertRow).where(
                    AlertRow.message == message
                )
            )

            db.commit()


def test_ingest_tracking_controls_reading_created():
    tracked_id = uuid4()
    disabled_id = uuid4()

    published_events = []

    try:
        with SessionLocal() as db:
            tracked_device = DeviceRow(
                id=tracked_id,
                device_type="moisture_sensor",
                role="sensor",
                device_family="simulation",
                display_name=(
                    "Phase 11 Tracked Sensor"
                ),
                default_config={
                    "protocol": "simulation",
                },
                tracking_enabled=True,
                sampling_interval_seconds=300,
            )

            disabled_device = DeviceRow(
                id=disabled_id,
                device_type="moisture_sensor",
                role="sensor",
                device_family="simulation",
                display_name=(
                    "Phase 11 Disabled Sensor"
                ),
                default_config={
                    "protocol": "simulation",
                },
                tracking_enabled=False,
                sampling_interval_seconds=300,
            )

            db.add_all(
                [
                    tracked_device,
                    disabled_device,
                ]
            )

            db.commit()

        event_bus = EventBus()

        event_bus.subscribe(
            ReadingCreated,
            published_events.append,
        )

        with SessionLocal() as db:
            service = ReadingIngest(
                device_repository=(
                    DeviceRepository(db)
                ),
                reading_repository=(
                    ReadingRepository(db)
                ),
                event_bus=event_bus,
            )

            service.record(
                tracked_id,
                translated_reading=Reading(
                    device_id=tracked_id,
                    value=0.41,
                    unit="vwc",
                    source="mqtt",
                    recorded_at=datetime.now(
                        timezone.utc
                    ),
                ),
            )

            service.record(
                disabled_id,
                translated_reading=Reading(
                    device_id=disabled_id,
                    value=0.42,
                    unit="vwc",
                    source="mqtt",
                    recorded_at=datetime.now(
                        timezone.utc
                    ),
                ),
            )

        assert len(published_events) == 1

        event = published_events[0]

        assert isinstance(
            event,
            ReadingCreated,
        )

        assert event.device_id == tracked_id
        assert event.value == 0.41
        assert event.unit == "vwc"
        assert event.source == "mqtt"

        with SessionLocal() as db:
            tracked_rows = db.scalars(
                select(ReadingRow).where(
                    ReadingRow.device_id
                    == tracked_id
                )
            ).all()

            disabled_rows = db.scalars(
                select(ReadingRow).where(
                    ReadingRow.device_id
                    == disabled_id
                )
            ).all()

            # Tracking off stops publishing,
            # but the reading is still stored.
            assert len(tracked_rows) == 1
            assert len(disabled_rows) == 1

    finally:
        with SessionLocal() as db:
            db.execute(
                delete(ReadingRow).where(
                    ReadingRow.device_id.in_(
                        [
                            tracked_id,
                            disabled_id,
                        ]
                    )
                )
            )

            db.execute(
                delete(DeviceRow).where(
                    DeviceRow.id.in_(
                        [
                            tracked_id,
                            disabled_id,
                        ]
                    )
                )
            )

            db.commit()


def test_low_moisture_creates_zone_alert():
    location_id = None
    sensor_id = None

    create_location_response = client.post(
        "/api/locations/config",
        json={
            "location_name": (
                f"Phase 11 Test Location "
                f"{uuid4()}"
            ),
            "zones": [
                {
                    "name": "Bench 1",
                    "moisture_threshold_low": 0.20,
                    "moisture_threshold_high": 0.60,
                    "schedule": {},
                },
                {
                    "name": "Bench 2",
                    "moisture_threshold_low": 0.25,
                    "moisture_threshold_high": 0.65,
                    "schedule": {},
                },
            ],
        },
    )

    assert (
        create_location_response.status_code
        == 201
    )

    location_data = (
        create_location_response.json()
    )

    location_id = (
        location_data["location"]["id"]
    )

    bench_1_id = (
        location_data["zones"][0]["id"]
    )

    bench_2_id = (
        location_data["zones"][1]["id"]
    )

    create_sensor_response = client.post(
        "/api/sensors",
        json={
            "type": "moisture",
            "display_name": (
                "Phase 11 Bench 1 Sensor"
            ),
        },
    )

    assert (
        create_sensor_response.status_code
        == 201
    )

    sensor_id = (
        create_sensor_response.json()["id"]
    )

    try:
        assign_response = client.patch(
            f"/api/devices/{sensor_id}/zone",
            json={
                "zone_id": bench_1_id,
            },
        )

        assert assign_response.status_code == 200

        with SessionLocal() as db:
            device = db.get(
                DeviceRow,
                UUID(sensor_id),
            )

            assert device is not None

            device.tracking_enabled = True

            db.commit()

        with SessionLocal() as db:
            service = ReadingIngest(
                device_repository=(
                    DeviceRepository(db)
                ),
                reading_repository=(
                    ReadingRepository(db)
                ),
                event_bus=build_event_bus(db),
            )

            service.record(
                UUID(sensor_id),
                translated_reading=Reading(
                    device_id=UUID(sensor_id),
                    value=0.10,
                    unit="vwc",
                    source="mqtt",
                    recorded_at=datetime.now(
                        timezone.utc
                    ),
                ),
            )

        bench_1_response = client.get(
            "/api/alerts",
            params={
                "zone_id": bench_1_id,
                "status": "active",
            },
        )

        assert bench_1_response.status_code == 200

        bench_1_alerts = (
            bench_1_response.json()
        )

        matching_alerts = [
            alert
            for alert in bench_1_alerts
            if (
                alert["device_id"]
                == sensor_id
                and alert["event_type"]
                == "threshold.crossed"
            )
        ]

        assert len(matching_alerts) >= 1

        alert = matching_alerts[0]

        assert (
            alert["location_id"]
            == location_id
        )

        assert (
            alert["zone_id"]
            == bench_1_id
        )

        assert alert["severity"] == "warning"

        assert (
            alert["message"]
            == "Moisture below zone low"
        )

        bench_2_response = client.get(
            "/api/alerts",
            params={
                "zone_id": bench_2_id,
                "status": "active",
            },
        )

        assert bench_2_response.status_code == 200

        bench_2_alerts = (
            bench_2_response.json()
        )

        assert not any(
            alert["device_id"] == sensor_id
            for alert in bench_2_alerts
        )

    finally:
        if sensor_id is not None:
            sensor_uuid = UUID(sensor_id)

            with SessionLocal() as db:
                db.execute(
                    delete(AlertRow).where(
                        AlertRow.device_id
                        == sensor_uuid
                    )
                )

                db.execute(
                    delete(ReadingRow).where(
                        ReadingRow.device_id
                        == sensor_uuid
                    )
                )

                db.execute(
                    delete(DeviceRow).where(
                        DeviceRow.id
                        == sensor_uuid
                    )
                )

                db.commit()

        if location_id is not None:
            client.delete(
                f"/api/locations/{location_id}"
            )


def test_failed_unassigned_command_creates_alert(
    monkeypatch,
):
    device_id = uuid4()

    try:
        with SessionLocal() as db:
            device = DeviceRow(
                id=device_id,
                device_type="water_pump",
                role="actuator",
                device_family="simulation",
                display_name=(
                    "Phase 11 Unassigned Pump"
                ),
                default_config={
                    "protocol": "simulation",
                },
                tracking_enabled=False,
                sampling_interval_seconds=300,
            )

            state = ActuatorStateRow(
                device_id=device_id,
                state="idle",
            )

            db.add(device)
            db.flush()

            db.add(state)
            db.commit()

        with SessionLocal() as db:
            service = CommandService(db)

            def fail_execution(
                *args,
                **kwargs,
            ):
                raise RuntimeError(
                    "Max run time exceeded"
                )

            monkeypatch.setattr(
                service.invoker,
                "execute",
                fail_execution,
            )

            result = service.execute(
                CommandRequest(
                    command_type="start_pump",
                    device_id=device_id,
                    payload={},
                )
            )

            assert result.status == "failed"

            assert (
                result.error_message
                == "Max run time exceeded"
            )

        with SessionLocal() as db:
            statement = (
                select(AlertRow)
                .where(
                    AlertRow.device_id
                    == device_id
                )
                .where(
                    AlertRow.event_type
                    == "command.failed"
                )
                .order_by(
                    AlertRow.created_at.desc()
                )
            )

            alert = db.scalar(statement)

            assert alert is not None

            assert alert.location_id is None
            assert alert.zone_id is None

            assert alert.severity == "warning"

            assert (
                alert.message
                == "Max run time exceeded"
            )

    finally:
        with SessionLocal() as db:
            db.execute(
                delete(AlertRow).where(
                    AlertRow.device_id
                    == device_id
                )
            )

            db.execute(
                delete(CommandLogRow).where(
                    CommandLogRow.device_id
                    == device_id
                )
            )

            db.execute(
                delete(ActuatorStateRow).where(
                    ActuatorStateRow.device_id
                    == device_id
                )
            )

            db.execute(
                delete(DeviceRow).where(
                    DeviceRow.id
                    == device_id
                )
            )

            db.commit()


def test_transition_to_error_creates_critical_alert():
    device_id = uuid4()

    try:
        with SessionLocal() as db:
            device = DeviceRow(
                id=device_id,
                device_type="water_pump",
                role="actuator",
                device_family="simulation",
                display_name=(
                    "Phase 11 Error Test Pump"
                ),
                default_config={
                    "protocol": "simulation",
                },
                tracking_enabled=False,
                sampling_interval_seconds=300,
            )

            state = ActuatorStateRow(
                device_id=device_id,
                state="idle",
            )

            db.add(device)
            db.flush()

            db.add(state)
            db.commit()

        response = client.post(
            f"/api/devices/{device_id}/transition",
            json={
                "target": "error",
            },
        )

        assert response.status_code == 200

        state_data = response.json()

        assert state_data["state"] == "error"

        with SessionLocal() as db:
            statement = (
                select(AlertRow)
                .where(
                    AlertRow.device_id
                    == device_id
                )
                .where(
                    AlertRow.event_type
                    == "state.changed"
                )
                .order_by(
                    AlertRow.created_at.desc()
                )
            )

            alert = db.scalar(statement)

            assert alert is not None

            assert alert.severity == "critical"

            assert (
                alert.message
                == "Actuator entered error"
            )

    finally:
        with SessionLocal() as db:
            db.execute(
                delete(AlertRow).where(
                    AlertRow.device_id
                    == device_id
                )
            )

            db.execute(
                delete(ActuatorStateRow).where(
                    ActuatorStateRow.device_id
                    == device_id
                )
            )

            db.execute(
                delete(DeviceRow).where(
                    DeviceRow.id
                    == device_id
                )
            )

            db.commit()


def test_publishers_do_not_import_alert_repository():
    publisher_files = [
        Path(
            "src/application/readings/service.py"
        ),
        Path(
            "src/application/commands/service.py"
        ),
        Path(
            "src/application/actuators/service.py"
        ),
    ]

    for file_path in publisher_files:
        source = file_path.read_text(
            encoding="utf-8"
        )

        assert (
            "AlertRepository"
            not in source
        ), (
            f"{file_path} must publish "
            "events instead of importing "
            "AlertRepository"
        )