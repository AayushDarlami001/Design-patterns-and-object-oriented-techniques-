from src.domain.sensors.creators import (
    LightSensorCreator,
    MoistureSensorCreator,
    get_sensor_creator,
)


def test_moisture_sensor_defaults():
    creator = MoistureSensorCreator()
    sensor = creator.create_sensor()

    assert sensor.device_type == "moisture_sensor"
    assert sensor.default_config["unit"] == "%"
    assert "moisture_threshold" in sensor.default_config


def test_light_sensor_defaults():
    creator = LightSensorCreator()
    sensor = creator.create_sensor()

    assert sensor.device_type == "light_sensor"
    assert sensor.default_config["unit"] == "lux"
    assert "moisture_threshold" not in sensor.default_config


def test_unknown_sensor_type():
    try:
        get_sensor_creator("unknown")
        assert False
    except ValueError:
        assert True