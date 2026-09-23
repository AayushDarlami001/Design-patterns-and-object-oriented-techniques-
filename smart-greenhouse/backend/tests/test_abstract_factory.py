from src.domain.devices.family_factory import (
    EdgeDeviceFactory,
    SimulationDeviceFactory,
)


def test_simulation_factory_creates_four_devices():
    factory = SimulationDeviceFactory()

    devices = factory.create_device_set()

    assert len(devices) == 4
    assert all(device.device_family == "simulation" for device in devices)


def test_simulation_factory_has_sensors_and_actuators():
    factory = SimulationDeviceFactory()

    devices = factory.create_device_set()

    roles = {device.role for device in devices}

    assert "sensor" in roles
    assert "actuator" in roles


def test_edge_factory_differs_from_simulation():
    simulation_devices = SimulationDeviceFactory().create_device_set()
    edge_devices = EdgeDeviceFactory().create_device_set()

    assert all(
        device.device_family == "simulation"
        for device in simulation_devices
    )

    assert all(
        device.device_family == "edge"
        for device in edge_devices
    )

    simulation_protocols = {
        device.default_config.get("protocol")
        for device in simulation_devices
    }

    edge_protocols = {
        device.default_config.get("protocol")
        for device in edge_devices
    }

    assert simulation_protocols != edge_protocols