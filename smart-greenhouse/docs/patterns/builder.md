# Builder

## Problem

A location configuration contains a location name and one or more zones. Each zone also needs valid moisture thresholds and an optional schedule.

Creating all of this directly in the API would make validation and object construction harder to manage.

## Solution

I used the Builder pattern with `LocationConfigBuilder`.

The builder:

- sets the location name
- adds zones
- validates the configuration
- returns a complete `LocationConfig`

If the configuration is invalid, it raises `ConfigurationError` before anything is saved to the database.

## Why Builder is used

Factory Method creates one type of object.

Abstract Factory creates a family of related devices.

Builder is different because it creates one complex object step by step.

In this phase, the complex object is the location configuration containing a location and its zones.

## Validation

Validation is handled in the domain layer.

The builder checks:

- location name is not empty
- at least one zone exists
- zone names are unique
- moisture thresholds are between 0.0 and 1.0
- low threshold is lower than high threshold

This prevents invalid configurations from reaching the database.

## Why location_id is used

The project uses `location_id` because zones belong to a location.

Each zone stores the location it belongs to, and devices can also store the related location when assigned to a zone.

The project does not use `greenhouse_id` in this phase.

## Device assignment

Device assignment is not part of the Builder.

The builder creates a new location configuration before the zones have database IDs.

After the location and zones are saved, a separate assignment service can assign an existing device to a zone.

When a device is assigned, its `zone_id` and `location_id` are updated together.

## Main files

- `domain/locations/entity.py`
- `domain/locations/config_builder.py`
- `domain/locations/errors.py`
- `application/locations/dto.py`
- `application/locations/mappers.py`
- `application/locations/config_service.py`
- `application/locations/zone_assignment_service.py`
- `infrastructure/persistence/location_repository.py`
- `interfaces/api/locations.py`