# Facade Pattern

## Problem

The dashboard needs information from several parts of the greenhouse system at the same time.

Without a Facade, the overview API or frontend would need to separately load:

- location information
- zones
- assigned devices
- latest sensor readings
- saved automation strategy
- latest automation recommendation

That would make the router or frontend responsible for coordinating too many subsystems.

The Facade pattern gives the dashboard one simple entry point for this combined information.

## Solution

Phase 7 introduces `LocationOverviewFacade`.

The facade provides one main operation:

`get_overview(location_id)`

It coordinates the existing repositories and automation service and returns one `LocationOverviewDto`.

The HTTP route does not directly work with device, reading, location, or automation repositories.

The router only calls the Facade.

## Facade Entry Point

The overview endpoint is:

`GET /api/locations/{location_id}/overview`

It returns one complete dashboard snapshot for the selected location.

The response contains:

- location information
- assigned device counts
- every zone
- assigned devices for each zone
- latest readings for those devices
- saved strategy key
- latest recommendation

## Location Scope

The overview is always scoped by `location_id`.

There is no `greenhouse_id`.

Only devices that:

- belong to the selected location
- have a non-null `zone_id`

are considered assigned devices.

Unassigned devices are not included in:

- `device_counts`
- `zones[].devices`
- `zones[].latest_readings`

## Device Counts

The facade counts assigned devices by role.

The current response contains:

- sensor count
- actuator count

These counts do not include unassigned devices.

## Zones

Every zone belonging to the selected location is included in the overview.

This includes zones that have no assigned devices.

For an empty zone:

`devices` is an empty list.

`latest_readings` is also an empty list.

This allows the dashboard to still show the full location structure.

## Latest Readings

For assigned devices, the overview repository loads the newest reading for each device.

The newest reading is selected using `recorded_at`.

The reading can come from any existing Phase 5 ingest path, such as:

- manual sensor read
- simulation sampler
- MQTT-translated reading

The Facade does not care how the reading originally entered the database.

It only uses the latest persisted reading.

## Reading Summary

The overview reading contains:

- `device_id`
- `value`
- `unit`
- `recorded_at`
- `tracking_enabled`
- `sampling_interval_seconds`

The tracking flag and sampling interval come from the device.

They are not stored again in `sensor_readings`.

## Strategy

The Facade loads the saved `strategy_key` for the selected location.

If no strategy has been saved, the overview still returns HTTP 200.

In that case:

`strategy_key = null`

and:

`last_recommendation = null`

A missing strategy is not treated as a missing location.

## Last Recommendation

When a strategy key exists, the Facade calls the existing Phase 6 automation evaluation service.

The Facade does not duplicate conservative or aggressive decision logic.

The existing Strategy implementation still decides the recommendation.

The overview only returns:

- action
- reason

The recommendation is computed each time the overview endpoint is requested.

It is not stored in a new database table.

## Query Shape

The Facade uses repository queries to avoid unnecessary database calls.

The main overview flow is:

1. Load the location.
2. Load all zones for the location.
3. Load assigned devices for the location.
4. Load the newest readings for those device IDs.
5. Load the saved strategy key.
6. Call automation evaluation only when a strategy exists.
7. Build one `LocationOverviewDto`.

The reading repository query uses one query for the device IDs rather than running one reading query for every device.

The automation evaluation service may still load moisture data per zone because that behavior already belongs to the Phase 6 Strategy workflow.

The Facade does not reimplement that logic.

## No New Database Table

Phase 7 does not require a new business table.

The existing tables are enough:

- `locations`
- `zones`
- `devices`
- `sensor_readings`
- `automation_rules`

No Alembic migration was needed for this phase.

## Frontend

The dashboard Overview section uses the single overview endpoint.

React does not separately fetch:

- devices
- readings
- automation data

and merge them into one dashboard model.

Instead, it calls:

`GET /api/locations/{location_id}/overview`

and renders the returned DTO.

The user can:

- select a location
- refresh the overview
- see assigned sensor and actuator counts
- see the current strategy
- see the current recommendation
- see all zones
- see assigned devices
- see latest readings when available

## Main Files

The Facade implementation is located in:

- `application/overview/dto.py`
- `application/overview/facade.py`
- `infrastructure/persistence/overview_repository.py`
- `interfaces/api/overview.py`
- `frontend/src/components/overview/OverviewPanel.tsx`

## Why Facade Helps

Facade hides the complexity of several existing greenhouse subsystems behind one simpler interface.

The API route does not need to understand how locations, devices, readings, and automation are stored or evaluated.

The frontend also receives one ready-to-use read model instead of coordinating several API calls.

This keeps the overview code simpler and prevents dashboard-specific coordination logic from spreading across the router and React components.