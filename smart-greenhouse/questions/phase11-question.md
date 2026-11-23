# Phase 11 — Observer questions

## A. Pattern

### 1. State the intent of Observer in plain language. What is a one-to-many dependency here, and why must the subject notify dependents without knowing their concrete classes?

The intent of Observer is to let one part of the system announce that something happened so several other parts can react without being directly connected to the publisher. A one-to-many dependency means that one event can have many subscribers. In our greenhouse, one event such as `reading.created` can cause threshold checking, alert creation, metrics, or later WebSocket updates.

The publisher should not know the concrete subscriber classes because that would create tight coupling. With Observer, new subscribers can be added without changing the publisher.

---

### 2. Name the participants (subject / event bus, observer / subscriber, concrete observers, event, publisher). What does subscribe / unsubscribe / publish (or notify) each do? This example’s EventBus implements subscribe and publish only.

The **subject** in this phase is the `EventBus`. The **observers** are subscribers that react to events. Concrete observers include `MoistureThresholdSubscriber` and `AlertPersistenceSubscriber`. The **events** include `ReadingCreated`, `ThresholdCrossed`, `CommandFailed`, and `ActuatorStateChanged`. Publishers include `ReadingIngest`, `CommandService`, and actuator state transition services.

`subscribe` registers a handler for an event type. `unsubscribe` would remove a registered observer, although our Phase 11 `EventBus` does not implement it. `publish` sends an event to all handlers subscribed to that event type.

---

### 3. When should you use Observer, and when should you skip it?

Observer is useful when one domain action can cause several independent reactions and when new listeners may be added later. It is also useful when we want to add things such as alerts, metrics, logging, or WebSocket updates without modifying the original publisher.

I would skip Observer when there will only ever be one simple listener because a direct method call is easier. I would also avoid it for a strict multi-step workflow where operations must happen in a guaranteed complex order, because an explicit workflow or queue would be clearer.

## B. This phase of the application

### 4. Give at least two domain events you publish in this lab...

The domain events in this phase include `ReadingCreated`, `ThresholdCrossed`, `CommandFailed`, and `ActuatorStateChanged`.

`ReadingIngest` publishes `reading.created` after successfully storing a reading, but only when the device has `tracking_enabled = true`. Manual reading, the simulation sampler, and MQTT-translated readings all use the same `ReadingIngest` path, so they follow one consistent publishing rule.

The publisher must not import `AlertRepository` or UI code because its responsibility is only to perform its domain action and publish an event. Subscribers decide what should happen afterward. This keeps the publisher independent from alert persistence and presentation code.

---

### 5. What does AlertPersistenceSubscriber do when it handles an event?

`AlertPersistenceSubscriber` listens for important events and converts them into persistent alert rows.

For `threshold.crossed`, it stores a `warning` alert with the message `Moisture below zone low`. For `command.failed`, it stores a `warning` alert using the failure message, such as `Max run time exceeded`. For `state.changed`, it stores a `critical` alert with the message `Actuator entered error`, but only when the actuator state becomes `error`.

The alerts are stored in the `alerts` database table so they are not lost when the React page refreshes. The Event Feed can request the stored alerts again from `GET /api/alerts`.

---

### 6. The dashboard Event feed polls GET /api/alerts every 5 seconds...

Full WebSocket support is not required in Phase 11 because the purpose of this phase is to implement the Observer pattern and persistent alerts. The dashboard can already show new alerts by polling `GET /api/alerts` every five seconds, while `realtime.ts` is only a placeholder for the next phase.

In Phase 12, the WebSocket functionality should subscribe to the same existing event bus instead of creating another pub/sub system inside the socket handlers. This allows the WebSocket to become another observer of the existing domain events. For example, after an alert is inserted, an `AlertCreated` event can be published and sent to connected dashboards.

---

### 7. Describe the must-demo path...

A tracked moisture sensor first produces a reading through `ReadingIngest`. The reading is stored and `ReadingCreated` is published to the `EventBus`. `MoistureThresholdSubscriber` checks the reading against the zone's low threshold. If it is below the threshold, it publishes `ThresholdCrossed`.

`AlertPersistenceSubscriber` receives that event and writes the alert to the `alerts` table. `GET /api/alerts` then returns the alert, and the dashboard Event Feed displays it on its next five-second poll.

`ReadingIngest` must not write the alert directly because alert creation belongs to the subscriber. When `tracking_enabled` is false, the reading may still be stored in `sensor_readings`, but `ReadingCreated` is not published, so this Observer event chain does not start.

## C. Compare, contrast, and scenarios

### 8. Contrast Observer with Facade.

Facade and Observer solve different problems. Facade provides one simple entry point for calling several parts of a subsystem. Observer sends notifications outward to several interested subscribers after something happens.

In Phase 7, the greenhouse overview facade combines information such as locations, devices, readings, and automation into one overview response for the dashboard. In Phase 11, the `EventBus` works in the opposite direction: a publisher announces an event and several subscribers can react independently.

---

### 9. Contrast Observer with Command.

Command represents an intention to perform an action, such as starting or stopping a water pump. Observer represents the outcome or event produced after something happens.

For example, `CommandService.execute()` performs a command. If execution fails, it publishes `CommandFailed`. The command itself does not need to know that `AlertPersistenceSubscriber` exists. The event bus connects the event to the subscriber, so the command classes remain focused on executing their actions. The course guide describes this as Command capturing intent while Observer propagates outcomes.

---

### 10. One subscriber throws during notify / publish and aborts the loop..

This is a problem because one broken subscriber could prevent every subscriber after it from receiving the event. For example, if the alert database writer fails, a metrics subscriber or future WebSocket subscriber should not automatically be prevented from receiving the same event.

A more robust event bus should isolate subscriber failures. It can catch an exception from one handler, record or log the failure, and continue notifying the remaining subscribers. For larger or slower workloads, handlers could also be moved to an asynchronous or queued system so one subscriber does not block the others.