# Abstract Factory

## Problem

The greenhouse needs different groups of devices for different environments. For example, simulation devices and edge devices need matching sensors, actuators, names, and configurations.

## Solution

I used the Abstract Factory pattern. Each device family factory creates a complete set of related devices.

The `SimulationDeviceFactory` creates devices for simulation, while the `EdgeDeviceFactory` creates devices with different settings for edge hardware.

Each family creates:

- Moisture sensor
- Light sensor
- Water pump
- Grow light

## Factory Method vs Abstract Factory

Factory Method from Phase 2 creates one sensor type at a time.

Abstract Factory in Phase 3 creates a complete family of related sensors and actuators.

The Phase 3 factories still use the Phase 2 sensor creators instead of replacing them.

## Where it is used

Main files:

- `domain/devices/entity.py`
- `domain/devices/family_factory.py`
- `application/devices/family_service.py`
- `application/devices/dto.py`
- `application/devices/mappers.py`
- `infrastructure/persistence/device_repository.py`
- `interfaces/api/devices.py`

## Device and DTO

`Device` is the domain object used inside the application.

`DeviceDto` is used for data returned through the API. Keeping them separate prevents API-specific code from entering the domain layer.

## Extension

A new family, such as a `cloud` family, could be added by creating another factory and registering it without changing the existing simulation and edge factories.