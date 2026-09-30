# Adapter

## Problem

Different sensor sources can provide data in different formats.

For example:

- simulation sensors generate values inside the application
- a vendor device can use its own payload field names
- MQTT data can arrive as a payload such as `value` and `unit`

If the application handled all of these formats directly, sensor-reading code would become tightly connected to each device or protocol.

## Solution

I used the Adapter pattern so all sensor sources are converted into the same `Reading` format.

The application works with `SensorPort` instead of depending directly on simulation, vendor, or MQTT code.

Each adapter converts its own source into:

- `device_id`
- `value`
- `unit`
- `source`
- `recorded_at`

## Sensor Port

`SensorPort` defines the common sensor read operation.

The application can use this port without knowing how the value was originally produced.

## Simulation Adapter

`SimulationSensorAdapter` generates sensor values in code.

Moisture values are generated between approximately `0.2` and `0.6 vwc`.

Light values are generated between approximately `200` and `2000 lux`.

The reading source is `simulation`.

## Vendor Stub Adapter

`VendorStubSensorAdapter` represents a vendor that uses a different payload format.

For example, it can receive:

`reading_value`

and

`reading_unit`

The adapter translates those fields into the common `Reading` object.

The reading source is `vendor`.

## MQTT Adapter

`MqttSensorAdapter` translates an MQTT-style payload such as:

`{ "value": 0.41, "unit": "vwc" }`

into the same `Reading` type.

The reading source is `mqtt`.

This phase does not connect to an MQTT broker. The adapter only performs the translation.

## Adapter Selection

The sensor adapter is selected from the device configuration.

- `protocol: simulation` uses the simulation adapter
- `protocol: mqtt` represents MQTT sensor data
- `adapter: vendor_stub` selects the vendor stub separately

The vendor stub uses its own flag so it does not conflict with the normal protocol selection.

## Reading Persistence

Every successful reading is stored in the `sensor_readings` table.

`ReadingIngest` is the common path used to save readings.

This means sensor history remains available after refreshing the application.

## Sampling

Simulation sensors can be read automatically.

Each device stores:

- `sampling_interval_seconds`
- `tracking_enabled`

The simulation sampler only reads simulation sensors when tracking is enabled and the configured interval has passed.

MQTT sensors and devices with tracking disabled are skipped.

## Actuator Port

Phase 5 also introduces `ActuatorPort`.

`SimulationActuatorAdapter` implements this port without controlling real hardware. It only records the requested action in memory.

This prepares the project for later phases where actuator behavior will be extended.

## Main Files

- `domain/sensors/reading.py`
- `domain/sensors/ports.py`
- `domain/actuators/ports.py`
- `infrastructure/adapters/sensors/simulation.py`
- `infrastructure/adapters/sensors/vendor_stub.py`
- `infrastructure/adapters/sensors/mqtt.py`
- `infrastructure/adapters/sensors/selector.py`
- `infrastructure/adapters/actuators/simulation.py`
- `application/readings/service.py`
- `application/readings/sampler.py`
- `infrastructure/persistence/reading_repository.py`
- `interfaces/api/sensors.py`
- `interfaces/api/devices.py`

## Extension

If another sensor vendor is added later, a new adapter can implement `SensorPort` and translate that vendor's format into the same `Reading`.

The application service does not need to change its main reading logic.