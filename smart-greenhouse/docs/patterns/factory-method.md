# Factory Method

## Problem

The greenhouse can have different types of sensors, such as moisture and light sensors. Each sensor has different default settings, so creating them directly in many places would make the code harder to maintain.

## Solution

I used the Factory Method pattern. `SensorCreator` defines how sensors are created, while `MoistureSensorCreator` and `LightSensorCreator` create their own sensor types with different default settings.

## Where it is used

The main files are:

- `domain/sensors/entity.py`
- `domain/sensors/creators.py`
- `application/sensors/service.py`

The API does not create the sensors directly. It asks the service, which uses the correct creator.

## Extension

In the future, a temperature sensor could be added by creating a new `TemperatureSensorCreator` without changing all the existing sensor creation code.# Factory Method

## Problem

The greenhouse can have different types of sensors, such as moisture and light sensors. Each sensor has different default settings, so creating them directly in many places would make the code harder to maintain.

## Solution

I used the Factory Method pattern. `SensorCreator` defines how sensors are created, while `MoistureSensorCreator` and `LightSensorCreator` create their own sensor types with different default settings.

## Where it is used

The main files are:

- `domain/sensors/entity.py`
- `domain/sensors/creators.py`
- `application/sensors/service.py`

The API does not create the sensors directly. It asks the service, which uses the correct creator.

## Extension

In the future, a temperature sensor could be added by creating a new `TemperatureSensorCreator` without changing all the existing sensor creation code.