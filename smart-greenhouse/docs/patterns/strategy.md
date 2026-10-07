# Strategy Pattern

## Problem

The greenhouse needs to make irrigation decisions from sensor readings and zone thresholds.

Different locations may use different decision rules. If the irrigation logic is written directly inside the API route or service with many `if strategy == ...` checks, the code becomes harder to maintain and extend.

The Strategy pattern lets the application choose between different automation algorithms through one common interface.

## Solution

Phase 6 uses an `AutomationStrategy` interface.

Each concrete strategy implements:

`decide(context)`

The strategy receives a plain `LocationAutomationContext` and returns a `Recommendation`.

The application service selects the saved strategy and calls the same `decide()` operation without needing to know the details of the algorithm.

## Context

`LocationAutomationContext` contains the information needed by a strategy:

- `location_id`
- `zone_id`
- latest moisture reading
- optional light reading
- zone moisture low threshold
- zone moisture high threshold

The context contains plain Python values.

Strategy classes do not use SQLAlchemy, FastAPI, repositories, or ORM rows.

## Recommendation

A strategy returns a `Recommendation`.

It contains:

- `action`
- `reason`
- optional `score`

Example actions are:

- `irrigate`
- `wait`

## Conservative Strategy

`ConservativeMoistureStrategy` waits until the moisture value is below the zone's low threshold.

Example:

- low threshold = 0.30
- high threshold = 0.50
- moisture = 0.40

Result:

`wait`

This strategy waits longer before recommending irrigation.

## Aggressive Strategy

`AggressiveMoistureStrategy` recommends irrigation when moisture is below the zone's high threshold.

Using the same example:

- low threshold = 0.30
- high threshold = 0.50
- moisture = 0.40

Result:

`irrigate`

This means the aggressive strategy starts irrigation earlier than the conservative strategy.

## Observable Difference

For the same context:

`moisture = 0.40`

with:

`low = 0.30`

and:

`high = 0.50`

the results are:

- Conservative → `wait`
- Aggressive → `irrigate`

This demonstrates that different Strategy implementations can be exchanged without changing the application service.

## Missing Sensor Reading

A zone is evaluated only from moisture sensors assigned to that zone.

If a zone has no assigned moisture sensor or no stored moisture reading, the result is:

`wait`

with a reason explaining that no moisture sensor reading is available.

The system does not borrow a reading from another zone or from an unassigned device.

## Persisted Strategy

The selected strategy is stored in the `automation_rules` table.

Each location has one active strategy because `location_id` is unique.

The stored strategy key is one of:

- `conservative`
- `aggressive`

The evaluation endpoint loads this persisted strategy before evaluating the location.

## Reading Source

Automation does not care how the reading was created.

The latest stored reading may come from:

- a manual sensor read
- the simulation sampler
- a translated MQTT reading

Phase 6 reads the latest data already stored in `sensor_readings`.

It does not create another sampling or MQTT pipeline.

## Application Flow

The automation evaluation works like this:

1. Receive a `location_id`.
2. Verify the location exists.
3. Load the saved strategy key.
4. Load every zone belonging to the location.
5. Find the latest moisture reading from sensors assigned to each zone.
6. Build a `LocationAutomationContext`.
7. Select the Strategy implementation.
8. Call `strategy.decide(context)`.
9. Convert the recommendation to an application DTO.
10. Return the result through the API.

## Main Files

The Strategy implementation is located in:

- `domain/automation/context.py`
- `domain/automation/strategy.py`
- `application/automation/dto.py`
- `application/automation/service.py`
- `infrastructure/persistence/automation_repository.py`
- `interfaces/api/automation.py`
- `frontend/src/features/automation/StrategyPanel.tsx`

The database configuration is stored in:

- `automation_rules`

## API

Phase 6 provides:

`GET /api/locations/{location_id}/automation`

Returns the active strategy.

`PUT /api/locations/{location_id}/automation`

Saves or changes the strategy.

`POST /api/locations/{location_id}/automation/evaluate`

Evaluates all zones using the persisted strategy.

Unknown strategy keys return a 400-level error.

A missing location returns 404.

## Adding a Third Strategy

A third strategy can be added by creating another class that implements `AutomationStrategy`.

For example:

`BalancedMoistureStrategy`

It could make its decision using the midpoint between the low and high thresholds.

After implementing the class, it can be registered in the strategy registry.

The API and automation service would not need new irrigation logic because they already depend on the common Strategy interface.

## Why Strategy Helps

The main benefit is that irrigation algorithms stay separate from API, persistence, and application orchestration.

New decision algorithms can be added without placing more business logic inside the router or rewriting the evaluation workflow.