# State Pattern

## Problem

Actuators can behave differently depending on their current state.

For example, a water pump in `idle` may be allowed to start, while a pump in `running` should not be allowed to start again.

If these rules are written separately inside routers or React components, the logic becomes duplicated and harder to maintain.

## Solution

The State pattern keeps the actuator lifecycle rules inside the domain layer.

The application stores the current actuator state in the database and asks the domain which transitions and commands are legal.

The API and frontend only use the result. They do not contain the transition rules themselves.

## States used

This phase uses these actuator states:

- `off`
- `idle`
- `running`
- `error`
- `maintenance`

## Transition rules

The current transition rules are:

- `off -> idle`
- `off -> maintenance`
- `off -> error`
- `idle -> running`
- `idle -> off`
- `idle -> maintenance`
- `idle -> error`
- `running -> idle`
- `running -> error`
- `error -> idle`
- `maintenance -> idle`
- `maintenance -> error`

Transitions that are not listed are rejected with `IllegalTransitionError`.

For example:

- `idle -> running` is valid.
- `running -> maintenance` is invalid.

An invalid transition does not update the stored database state.

## Allowed commands

The domain also derives `allowed_commands` from the current state.

Examples:

### idle

- `start_pump`
- `power_off`
- `enter_maintenance`
- `fault`

### running

- `stop_pump`
- `fault`

### error

- `reset`

These command names can be reused later by the Command pattern.

## Persistence

Actuator state is stored in the `actuator_states` table.

The table contains:

- `device_id`
- `state`
- `updated_at`

`device_id` is the primary key and references the actuator in the `devices` table.

Existing actuators were seeded with the initial state `idle` in the Phase 8 migration.

Because the state is stored in PostgreSQL, restarting the FastAPI application does not lose the actuator state.

## Where the pattern is implemented

### Domain

`src/domain/actuators/state.py`

Contains:

- valid states
- transition rules
- `get_allowed_commands()`
- `transition_state()`
- `IllegalTransitionError`

`src/domain/actuators/context.py`

Contains `ActuatorContext`, which holds the current state and delegates transition checks to the domain rules.

### Application

`src/application/actuators/service.py`

The service:

1. loads the actuator,
2. loads its persisted state,
3. creates the actuator context,
4. asks the domain to perform the transition,
5. saves the new state only if the transition is legal.

### Infrastructure

`src/infrastructure/persistence/actuator_state_repository.py`

Loads and saves actuator state in PostgreSQL.

### API

The application exposes:

- `GET /api/devices/{device_id}/state`
- `POST /api/devices/{device_id}/transition`

The normal device list also includes:

- `state`
- `allowed_commands`

A missing actuator returns `404`.

An illegal transition returns `409`.

### Frontend

Actuator cards in the Devices section show:

- the current state badge,
- the allowed commands for that state.

Sensors do not show actuator state information.

The frontend does not decide which transitions are legal. It displays the state and commands returned by the backend.

## Example

If the actuator is currently:

```text
idle