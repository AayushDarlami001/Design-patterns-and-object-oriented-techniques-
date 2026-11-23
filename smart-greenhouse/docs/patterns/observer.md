# Observer Pattern

## Intent

The Observer pattern is used in the Smart Greenhouse application to allow different parts of the system to react to events without tightly coupling publishers to the code that handles those events.

Phase 11 introduces an in-process `EventBus` that supports publish/subscribe communication.

Publishers create domain events and publish them to the event bus. Subscribers listen for specific event types and react when those events occur.

This keeps reading ingestion, actuator commands, state transitions, and alert persistence separated from each other.

## Participants

### EventBus

`EventBus` is responsible for registering subscribers and publishing events.

It provides:

- `subscribe(event_type, handler)`
- `publish(event)`

Handlers registered for an event type are executed in subscription order.

The Phase 11 event bus is in-process only. It does not use WebSockets or an external message broker.

## Domain Events

The application currently uses the following domain events.

### ReadingCreated

Published after a sensor reading is successfully stored when the device has `tracking_enabled = true`.

The event contains:

- `device_id`
- `location_id`
- `zone_id`
- `value`
- `unit`
- `source`
- `recorded_at`

Manual reads, the simulation sampler, and translated MQTT readings use the same ingest path.

If tracking is disabled, the reading may still be stored, but `ReadingCreated` is not published.

### ThresholdCrossed

Published by `MoistureThresholdSubscriber`.

The subscriber reacts to `ReadingCreated` only when:

- the reading unit is `vwc`
- the device has a zone
- the reading value is strictly below the zone's `moisture_threshold_low`

A reading from an unassigned device does not generate a threshold event.

### CommandFailed

Published by `CommandService` when actuator command execution actually fails.

Rejected commands are not considered execution failures and therefore do not publish `CommandFailed`.

For example, the maximum runtime decorator can cause a water pump command to fail with:

`Max run time exceeded`

### ActuatorStateChanged

Published after an actuator state has been successfully persisted.

The event contains the previous state and the new state together with the actuator's device, location, and zone identifiers.

The alert subscriber creates a critical alert only when the new state is `error`.

## Subscribers

### MoistureThresholdSubscriber

`MoistureThresholdSubscriber` listens for `ReadingCreated`.

It checks the zone's moisture threshold and publishes `ThresholdCrossed` when the moisture value is below the configured low threshold.

This subscriber does not persist alerts directly.

### AlertPersistenceSubscriber

`AlertPersistenceSubscriber` converts important domain events into persistent alert rows.

The mappings are:

- `threshold.crossed` → severity `warning` → `Moisture below zone low`
- `command.failed` → severity `warning` → command failure message
- `state.changed` to `error` → severity `critical` → `Actuator entered error`

Alerts are stored in the database so they remain available after the dashboard is refreshed.

## Event Flow

A moisture alert follows this flow:

`ReadingIngest`

→ publishes `ReadingCreated`

→ `MoistureThresholdSubscriber`

→ publishes `ThresholdCrossed`

→ `AlertPersistenceSubscriber`

→ stores an alert in the `alerts` table

A failed actuator command follows this flow:

`CommandService`

→ command execution fails

→ publishes `CommandFailed`

→ `AlertPersistenceSubscriber`

→ stores a warning alert

An actuator error transition follows this flow:

`ActuatorStateService` or `CommandService`

→ state is successfully stored

→ publishes `ActuatorStateChanged`

→ `AlertPersistenceSubscriber`

→ stores a critical alert when the new state is `error`

## Location and Zone Information

`location_id` and `zone_id` are copied from the device when the event is published.

The event does not perform a later lookup to invent this information.

If a device is unassigned, both values remain `null`.

This is important for events such as a failed command from an unassigned water pump.

## Decoupling

The main advantage of Observer in this phase is reduced coupling.

`ReadingIngest`, `CommandService`, and actuator state services do not call `AlertRepository` directly.

Instead, they publish domain events.

Alert persistence is handled by subscribers.

This means another subscriber can be added later without changing the publisher.

For example, logging, metrics, notifications, or WebSocket broadcasting can subscribe to the same events.

## Persistent Event Feed

The dashboard's `EventFeed` calls:

`GET /api/alerts`

The feed polls the endpoint every five seconds.

It supports filtering by:

- location
- zone

Because alerts are stored in PostgreSQL, refreshing the frontend does not remove them.

## Phase 12 Handoff

Phase 11 does not implement WebSocket communication.

`frontend/src/services/realtime.ts` contains only the realtime interface and a no-op subscription function.

Phase 12 can replace this implementation with a WebSocket connection and broadcast the same domain events without changing the core Observer publishers.

This demonstrates one of the main advantages of the Observer pattern: new subscribers can be introduced without tightly coupling them to the event producers.