from datetime import datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import delete

from src.infrastructure.db import SessionLocal
from src.infrastructure.persistence.models import (
    AutomationRuleRow,
    DeviceRow,
    LocationRow,
    ReadingRow,
    ZoneRow,
)
from src.main import app


client = TestClient(app)


def test_overview_returns_strategy_and_readings():
    location_id = None
    zone_1_id = None
    zone_2_id = None
    assigned_sensor_id = None
    unassigned_device_id = None

    try:
        with SessionLocal() as db:
            location = LocationRow(
                name="Phase 7 Test Greenhouse",
            )

            db.add(location)
            db.flush()

            location_id = location.id

            zone_1 = ZoneRow(
                location_id=location_id,
                name="Phase 7 Zone 1",
                moisture_threshold_low=0.30,
                moisture_threshold_high=0.50,
                schedule={},
            )

            zone_2 = ZoneRow(
                location_id=location_id,
                name="Phase 7 Empty Zone",
                moisture_threshold_low=0.25,
                moisture_threshold_high=0.55,
                schedule={},
            )

            db.add_all(
                [
                    zone_1,
                    zone_2,
                ]
            )

            db.flush()

            zone_1_id = zone_1.id
            zone_2_id = zone_2.id

            assigned_sensor = DeviceRow(
                device_type="moisture_sensor",
                role="sensor",
                device_family="simulation",
                display_name="Phase 7 Moisture Sensor",
                default_config={
                    "protocol": "simulation",
                    "unit": "vwc",
                },
                location_id=location_id,
                zone_id=zone_1_id,
                sampling_interval_seconds=120,
                tracking_enabled=False,
            )

            unassigned_device = DeviceRow(
                device_type="light_sensor",
                role="sensor",
                device_family="simulation",
                display_name="Phase 7 Unassigned Sensor",
                default_config={
                    "protocol": "simulation",
                    "unit": "lux",
                },
                location_id=location_id,
                zone_id=None,
                sampling_interval_seconds=300,
                tracking_enabled=False,
            )

            db.add_all(
                [
                    assigned_sensor,
                    unassigned_device,
                ]
            )

            db.flush()

            assigned_sensor_id = (
                assigned_sensor.id
            )

            unassigned_device_id = (
                unassigned_device.id
            )

            older_reading = ReadingRow(
                device_id=assigned_sensor_id,
                value=0.35,
                unit="vwc",
                source="simulation",
                recorded_at=datetime(
                    2026,
                    10,
                    14,
                    10,
                    0,
                    tzinfo=timezone.utc,
                ),
            )

            newest_reading = ReadingRow(
                device_id=assigned_sensor_id,
                value=0.40,
                unit="vwc",
                source="simulation",
                recorded_at=datetime(
                    2026,
                    10,
                    14,
                    10,
                    5,
                    tzinfo=timezone.utc,
                ),
            )

            db.add_all(
                [
                    older_reading,
                    newest_reading,
                ]
            )

            db.commit()

        unknown_location_id = uuid4()

        unknown_response = client.get(
            (
                "/api/locations/"
                f"{unknown_location_id}"
                "/overview"
            )
        )

        assert (
            unknown_response.status_code
            == 404
        )

        overview_response = client.get(
            (
                "/api/locations/"
                f"{location_id}"
                "/overview"
            )
        )

        assert (
            overview_response.status_code
            == 200
        )

        overview = overview_response.json()

        assert (
            overview["location"]["id"]
            == str(location_id)
        )

        assert (
            overview["location"]["name"]
            == "Phase 7 Test Greenhouse"
        )

        assert (
            overview["strategy_key"]
            is None
        )

        assert (
            overview[
                "last_recommendation"
            ]
            is None
        )

        assert (
            overview["device_counts"][
                "sensor"
            ]
            == 1
        )

        assert (
            overview["device_counts"][
                "actuator"
            ]
            == 0
        )

        assert (
            len(overview["zones"])
            == 2
        )

        zone_1_result = next(
            zone
            for zone in overview["zones"]
            if zone["id"]
            == str(zone_1_id)
        )

        zone_2_result = next(
            zone
            for zone in overview["zones"]
            if zone["id"]
            == str(zone_2_id)
        )

        assert (
            len(zone_1_result["devices"])
            == 1
        )

        assert (
            zone_1_result["devices"][0][
                "id"
            ]
            == str(assigned_sensor_id)
        )

        all_device_ids = {
            device["id"]
            for zone in overview["zones"]
            for device in zone["devices"]
        }

        assert (
            str(unassigned_device_id)
            not in all_device_ids
        )

        assert (
            zone_2_result["devices"]
            == []
        )

        assert (
            zone_2_result[
                "latest_readings"
            ]
            == []
        )

        assert (
            len(
                zone_1_result[
                    "latest_readings"
                ]
            )
            == 1
        )

        reading = zone_1_result[
            "latest_readings"
        ][0]

        assert (
            reading["device_id"]
            == str(assigned_sensor_id)
        )

        assert (
            reading["value"]
            == 0.40
        )

        assert (
            reading["unit"]
            == "vwc"
        )

        assert (
            reading[
                "tracking_enabled"
            ]
            is False
        )

        assert (
            reading[
                "sampling_interval_seconds"
            ]
            == 120
        )

        save_strategy_response = (
            client.put(
                (
                    "/api/locations/"
                    f"{location_id}"
                    "/automation"
                ),
                json={
                    "strategy_key":
                        "aggressive"
                },
            )
        )

        assert (
            save_strategy_response
            .status_code
            == 200
        )

        evaluate_response = client.post(
            (
                "/api/locations/"
                f"{location_id}"
                "/automation/evaluate"
            )
        )

        assert (
            evaluate_response.status_code
            == 200
        )

        evaluation = (
            evaluate_response.json()
        )

        second_overview_response = (
            client.get(
                (
                    "/api/locations/"
                    f"{location_id}"
                    "/overview"
                )
            )
        )

        assert (
            second_overview_response
            .status_code
            == 200
        )

        second_overview = (
            second_overview_response.json()
        )

        assert (
            second_overview[
                "strategy_key"
            ]
            == "aggressive"
        )

        assert (
            second_overview[
                "last_recommendation"
            ]
            is not None
        )

        assert (
            second_overview[
                "last_recommendation"
            ]["action"]
            == evaluation["action"]
        )

        assert (
            second_overview[
                "last_recommendation"
            ]["reason"]
            == evaluation["reason"]
        )

    finally:
        if location_id is not None:
            with SessionLocal() as db:
                db.execute(
                    delete(
                        AutomationRuleRow
                    ).where(
                        AutomationRuleRow
                        .location_id
                        == location_id
                    )
                )

                if (
                    assigned_sensor_id
                    is not None
                ):
                    db.execute(
                        delete(
                            ReadingRow
                        ).where(
                            ReadingRow
                            .device_id
                            == assigned_sensor_id
                        )
                    )

                if (
                    unassigned_device_id
                    is not None
                ):
                    db.execute(
                        delete(
                            ReadingRow
                        ).where(
                            ReadingRow
                            .device_id
                            == unassigned_device_id
                        )
                    )

                db.execute(
                    delete(
                        DeviceRow
                    ).where(
                        DeviceRow.location_id
                        == location_id
                    )
                )

                db.execute(
                    delete(
                        ZoneRow
                    ).where(
                        ZoneRow.location_id
                        == location_id
                    )
                )

                db.execute(
                    delete(
                        LocationRow
                    ).where(
                        LocationRow.id
                        == location_id
                    )
                )

                db.commit()