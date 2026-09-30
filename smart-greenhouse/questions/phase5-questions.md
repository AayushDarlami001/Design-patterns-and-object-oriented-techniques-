# Phase 5 — Adapter questions

## How to answer

- Use your own wording. Do not paste teaching-example types (for example a legacy XML calendar client) as if they were your greenhouse classes.
- When a question asks about *this application*, refer to sensor ports, adapters, readings, and `sensor_readings` from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of Adapter in plain language. What problem appears when business code speaks a vendor or legacy protocol (odd field names, units, XML, status codes) directly?

Adapter lets different external formats work through one common interface. If business code directly understands every vendor format, it becomes tightly connected to those vendors and becomes harder to change, test, or extend.

2. Name the participants (**target / port**, **adaptee**, **adapter**, **client**). What does the adapter translate, and what must it **not** decide (business policy)?

The target is the common port such as `SensorPort`. The adaptee is the original source, such as a vendor payload or MQTT-style payload. The adapter converts that source into the common `Reading`, and the client is the application service using the port. The adapter should only translate data and should not decide greenhouse business rules.

3. GoF distinguishes an **object adapter** (composition) from a **class adapter** (inheritance). Which does modern code prefer, and why?

Modern code usually prefers object adapters using composition. Composition gives more flexibility because the adapter can wrap or use another object without depending strongly on its inheritance structure.

## B. This phase of the application

4. What is `SensorPort` in this lab, and what normalized value type (for example `Reading`) do adapters return? Why do application services depend on the port rather than on a simulation driver or vendor SDK?

`SensorPort` is the common interface used for reading sensor data. The adapters return a normalized `Reading` containing the device ID, value, unit, source, and timestamp. Application services depend on the port so they can work with different sensor sources without knowing the details of simulation or vendor code.

5. You need three translations onto the same normalized reading: a simulation adapter, a vendor stub, and an MQTT translator that accepts a payload dict. Why is the different raw shape the point of the exercise? How does `source` (`simulation`, `vendor`, or `mqtt`) show which adapter produced the reading, and why must the MQTT translator not open a broker in this phase? Phase 12 may deliver that same dict on a device HTTP route or through an optional broker — why must this phase still not open either transport?

The different raw formats show why Adapter is useful. The simulation adapter generates a value, the vendor stub translates fields such as `reading_value`, and the MQTT adapter translates fields such as `value` and `unit` into the same `Reading`. The `source` field shows where the reading came from. The MQTT adapter only translates the payload in this phase, because HTTP and broker transport are separate responsibilities that are added later in Phase 12.

6. Readings are **appended** to `sensor_readings` (history grows). Why not keep only the latest value in memory or overwrite a single row, and which later phase consumes this history? Why do a manual read, the simulation sampler, and (later) MQTT share **one** writer of that table? Why does the sampler skip devices with tracking off and MQTT devices, and why do sensor cards poll the latest stored reading until Phase 12?

Readings are appended so the system keeps real history instead of losing older values when a new reading arrives. Phase 6 uses persisted sensor readings for greenhouse decisions, and later phases can also use the stored history. Manual reads, the simulation sampler, and later MQTT use the same `ReadingIngest` path so persistence stays consistent. The sampler skips tracking-disabled devices and MQTT devices because it should only generate simulation values. The frontend polls the stored latest reading temporarily until Phase 12 replaces polling with WebSocket updates.

7. `POST /api/sensors/{id}/read` runs an adapter, persists, and returns a DTO. What HTTP status is appropriate when the device is missing versus when the adapter fails? Why must the router never see vendor-shaped types?

A missing device should return `404`. An adapter or validation problem should return a `400` level error with useful detail. The router should only work with normal application DTOs because vendor-specific formats should be translated inside adapters, not exposed to the HTTP layer.

## C. Compare, contrast, and scenarios

8. Contrast Adapter with **Facade**. Adapter changes the **shape** of an existing interface; Facade simplifies **how to use** a subsystem. Give a greenhouse-shaped example of each (Adapter this phase; Facade in Phase 7).

Adapter changes incompatible sensor data into the common `Reading` format. For example, the vendor adapter converts `reading_value` and `reading_unit` into the same fields used by the rest of the application. A Facade would instead give the greenhouse application one simpler interface that hides several services or repositories behind it.

9. Contrast Adapter with **Decorator**. Both wrap an object. What is different about the interface they present to the client?

Adapter changes one interface into another interface that the client expects. Decorator normally keeps the same interface but adds extra behavior around the wrapped object. In this project, an adapter normalizes sensor input, while a later decorator can add behavior around an existing port.

10. A classmate puts irrigation policy (“if moisture < 0.3 then water”) inside the vendor adapter. Why is that a trap? Where should that decision live instead (later Strategy), and what should stay in the adapter?

Putting irrigation rules inside the adapter mixes data translation with business decisions. That would make the adapter harder to reuse and would connect vendor code to greenhouse policy. The irrigation decision should live in the later Strategy layer. The adapter should only translate the external sensor data into the normalized `Reading`.