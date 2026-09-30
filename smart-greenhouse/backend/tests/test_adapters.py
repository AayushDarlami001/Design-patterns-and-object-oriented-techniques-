from uuid import uuid4

from src.infrastructure.adapters.sensors.mqtt import MqttSensorAdapter
from src.infrastructure.adapters.sensors.simulation import (
    SimulationSensorAdapter,
)
from src.infrastructure.adapters.sensors.vendor_stub import (
    VendorStubSensorAdapter,
)


def test_simulation_moisture_range():
    adapter = SimulationSensorAdapter()

    reading = adapter.read(
        device_id=uuid4(),
        device_type="moisture_sensor",
        config={},
    )

    assert 0.2 <= reading.value <= 0.6
    assert reading.unit == "vwc"
    assert reading.source == "simulation"


def test_simulation_light_range():
    adapter = SimulationSensorAdapter()

    reading = adapter.read(
        device_id=uuid4(),
        device_type="light_sensor",
        config={},
    )

    assert 200 <= reading.value <= 2000
    assert reading.unit == "lux"
    assert reading.source == "simulation"


def test_vendor_translation():
    adapter = VendorStubSensorAdapter(
        {
            "reading_value": 0.44,
            "reading_unit": "vwc",
        }
    )

    reading = adapter.read(
        device_id=uuid4(),
        device_type="moisture_sensor",
        config={},
    )

    assert reading.value == 0.44
    assert reading.unit == "vwc"
    assert reading.source == "vendor"


def test_mqtt_translation():
    adapter = MqttSensorAdapter(
        {
            "value": 0.41,
            "unit": "vwc",
        }
    )

    reading = adapter.read(
        device_id=uuid4(),
        device_type="moisture_sensor",
        config={},
    )

    assert reading.value == 0.41
    assert reading.unit == "vwc"
    assert reading.source == "mqtt"