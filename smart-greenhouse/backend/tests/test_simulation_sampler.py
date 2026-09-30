from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from src.application.readings.dto import ReadingDto
from src.application.readings.sampler import SimulationSampler
from src.domain.devices.entity import Device


class FakeDeviceRepository:
    def __init__(self, devices):
        self.devices = devices

    def list_tracked_simulation_sensors(self):
        return [
            device
            for device in self.devices
            if device.role == "sensor"
            and device.tracking_enabled
            and device.default_config.get(
                "protocol",
                "simulation",
            )
            == "simulation"
        ]


class FakeReadingRepository:
    def __init__(self):
        self.latest_readings = {}

    def latest(self, device_id):
        return self.latest_readings.get(
            device_id
        )


class FakeIngest:
    def __init__(
        self,
        reading_repository,
    ):
        self.reading_repository = (
            reading_repository
        )

        self.recorded = []

    def record(
        self,
        device_id,
        translated_reading=None,
    ):
        assert translated_reading is not None

        self.recorded.append(
            translated_reading
        )

        self.reading_repository.latest_readings[
            device_id
        ] = translated_reading

        return ReadingDto(
            device_id=translated_reading.device_id,
            value=translated_reading.value,
            unit=translated_reading.unit,
            source=translated_reading.source,
            recorded_at=translated_reading.recorded_at,
        )


def make_device(
    protocol="simulation",
    tracking_enabled=True,
    interval=10,
):
    return Device(
        id=uuid4(),
        device_type="moisture_sensor",
        role="sensor",
        device_family="simulation",
        display_name="Test Sensor",
        default_config={
            "protocol": protocol,
        },
        sampling_interval_seconds=interval,
        tracking_enabled=tracking_enabled,
    )


def create_sampler(devices):
    device_repository = (
        FakeDeviceRepository(devices)
    )

    reading_repository = (
        FakeReadingRepository()
    )

    ingest = FakeIngest(
        reading_repository
    )

    sampler = SimulationSampler(
        device_repository=device_repository,
        reading_repository=reading_repository,
        ingest=ingest,
    )

    return (
        sampler,
        reading_repository,
        ingest,
    )


def test_sampler_records_first_reading():
    device = make_device()

    sampler, _, ingest = create_sampler(
        [device]
    )

    now = datetime.now(timezone.utc)

    result = sampler.run_once(now)

    assert len(result) == 1
    assert len(ingest.recorded) == 1

    assert (
        ingest.recorded[0].device_id
        == device.id
    )

    assert (
        ingest.recorded[0].source
        == "simulation"
    )


def test_sampler_skips_second_call_inside_interval():
    device = make_device(
        interval=10
    )

    sampler, _, ingest = create_sampler(
        [device]
    )

    start = datetime.now(timezone.utc)

    sampler.run_once(start)

    sampler.run_once(
        start + timedelta(seconds=5)
    )

    assert len(ingest.recorded) == 1


def test_sampler_records_after_interval():
    device = make_device(
        interval=10
    )

    sampler, _, ingest = create_sampler(
        [device]
    )

    start = datetime.now(timezone.utc)

    sampler.run_once(start)

    sampler.run_once(
        start + timedelta(seconds=11)
    )

    assert len(ingest.recorded) == 2


def test_sampler_skips_tracking_disabled():
    device = make_device(
        tracking_enabled=False
    )

    sampler, _, ingest = create_sampler(
        [device]
    )

    sampler.run_once(
        datetime.now(timezone.utc)
    )

    assert len(ingest.recorded) == 0


def test_sampler_skips_mqtt_device():
    device = make_device(
        protocol="mqtt"
    )

    sampler, _, ingest = create_sampler(
        [device]
    )

    sampler.run_once(
        datetime.now(timezone.utc)
    )

    assert len(ingest.recorded) == 0


def test_sampler_accepts_multiple_devices():
    first = make_device()
    second = make_device()

    sampler, _, ingest = create_sampler(
        [
            first,
            second,
        ]
    )

    sampler.run_once(
        datetime.now(timezone.utc)
    )

    assert len(ingest.recorded) == 2


def test_sampler_requires_timezone_aware_time():
    device = make_device()

    sampler, _, _ = create_sampler(
        [device]
    )

    naive_time = datetime.now()

    with pytest.raises(
        ValueError,
        match="timezone-aware",
    ):
        sampler.run_once(
            naive_time
        )