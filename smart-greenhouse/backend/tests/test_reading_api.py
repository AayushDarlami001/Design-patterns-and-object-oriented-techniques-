from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from src.infrastructure.db import SessionLocal
from src.infrastructure.persistence.models import (
    DeviceRow,
    ReadingRow,
)
from src.main import app


client = TestClient(app)


def test_sensor_read_persists_reading():
    create_response = client.post(
        "/api/sensors",
        json={
            "type": "moisture",
            "display_name": "Phase 5 Test Sensor",
        },
    )

    assert create_response.status_code == 201

    sensor = create_response.json()
    sensor_id = sensor["id"]

    try:
        read_response = client.post(
            f"/api/sensors/{sensor_id}/read"
        )

        assert read_response.status_code == 201

        reading = read_response.json()

        assert reading["device_id"] == sensor_id
        assert reading["source"] == "simulation"
        assert reading["unit"] == "vwc"

        with SessionLocal() as db:
            statement = select(ReadingRow).where(
                ReadingRow.device_id == sensor_id
            )

            rows = db.scalars(statement).all()

            assert len(rows) >= 1

            assert str(
                rows[-1].device_id
            ) == sensor_id

    finally:
        with SessionLocal() as db:
            db.execute(
                delete(ReadingRow).where(
                    ReadingRow.device_id == sensor_id
                )
            )

            db.execute(
                delete(DeviceRow).where(
                    DeviceRow.id == sensor_id
                )
            )

            db.commit()