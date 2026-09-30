from src.domain.sensors.ports import SensorPort
from src.infrastructure.adapters.sensors.simulation import (
    SimulationSensorAdapter,
)
from src.infrastructure.adapters.sensors.vendor_stub import (
    VendorStubSensorAdapter,
)


def select_sensor_adapter(
    config: dict,
) -> SensorPort:
    if config.get("adapter") == "vendor_stub":
        payload = config.get(
            "vendor_payload",
            {
                "reading_value": 0.42,
                "reading_unit": "vwc",
            },
        )

        return VendorStubSensorAdapter(
            payload
        )

    protocol = config.get(
        "protocol",
        "simulation",
    )

    if protocol == "simulation":
        return SimulationSensorAdapter()

    if protocol == "mqtt":
        raise ValueError(
            "MQTT sensor requires an inbound payload"
        )

    raise ValueError(
        f"Unsupported sensor protocol: {protocol}"
    )