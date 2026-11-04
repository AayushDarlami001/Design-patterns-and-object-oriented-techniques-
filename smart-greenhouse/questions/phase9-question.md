# Phase 9 — Decorator questions

## A. Pattern

### 1. State the intent of Decorator in plain language. Why is stacking wrappers a flexible alternative to a combinatorial explosion of subclasses (`LoggingRetryMaxRuntimeActuator`, …)?


Decorator adds extra behavior around an existing object without changing the original class. Stacking wrappers is more flexible because we can combine logging, max run-time, or other policies without creating a new subclass for every possible combination.


### 2. Name the participants (**component**, **concrete component**, **decorator**, **concrete decorators**). What interface does every decorator present to the caller, and why must that match the wrapped component?

The component is `ActuatorPort`, the concrete component is `SimulationActuatorAdapter`, and the concrete decorators are `LoggingActuatorDecorator` and `MaxRuntimeActuatorDecorator`. Every decorator still presents the same `ActuatorPort.apply(...)` interface, so the caller can use it without knowing whether it is talking to the adapter directly or through several wrappers.


### 3. **Order matters.** Using logging and retry (or logging and max-run-time) as an example, explain how wrapping A around B can change what you observe compared with wrapping B around A.

Order changes which decorator sees the call first. In my project, logging is outside max run-time, so it can record both successful calls and calls blocked by the max-run-time policy. If logging were inside the blocking decorator, a blocked request might never reach logging and would not be recorded.


## B. This phase of the application

### 4. What is `ActuatorPort` here, and which **at least two** decorators did you stack around the real adapter (for example logging and max run-time)? Where is the chain wired (composition root / factory), and why not inside the HTTP router?

`ActuatorPort` is the common interface used to apply commands to an actuator. I wrapped `SimulationActuatorAdapter` with `MaxRuntimeActuatorDecorator` and then `LoggingActuatorDecorator`. The chain is created in the `build_execution_service()` composition helper, while the route only calls the service. This keeps policy logic out of the HTTP handler.


### 5. Max run-time can **short-circuit**: the inner adapter is never called. Why must a blocked attempt still produce a row in `actuator_execution_log` with `success=false` and the policy named in `policy_applied`?

A blocked attempt is still an execution attempt, so it should be visible for debugging and monitoring. Saving `success=false` with `maxRunTime` shows exactly why the actuator was not called instead of making the attempt disappear from the history.


### 6. How does max run-time know the actuator has been running too long (for example `actuator_states.updated_at` from Phase 8)? Why is that data from **State**, not something the decorator should invent as a second lifecycle?

The max-run-time decorator reads the persisted actuator state and compares `actuator_states.updated_at` with the current time. If the actuator has been `running` for at least 30 minutes, it blocks the call. The lifecycle belongs to Phase 8 State, so the decorator should use that state instead of creating another separate idea of whether the actuator is running.


### 7. `GET /api/actuators/executions` feeds the dashboard execution log. Why persist attempts in the database instead of only printing to stdout? What should the UI show after a blocked attempt and a refresh?

Database records survive backend restarts and can be loaded again by the dashboard, while printed logs are not suitable as application history. After a blocked attempt and refresh, the UI should show `FAILED`, policies `maxRunTime, logging`, and the message `Max run time exceeded`.


## C. Compare, contrast, and scenarios

### 8. Contrast Decorator with **Adapter**. Both wrap. One **keeps** the interface and **adds** behaviour; the other **changes** the interface and **translates**. Which is which in this greenhouse (Phase 9 vs Phase 5)?

Decorator keeps the same interface and adds behavior. In Phase 9, the logging and max-run-time decorators still implement `ActuatorPort`. Adapter changes or translates another interface into the interface the application expects, like the sensor adapters from Phase 5.


### 9. Contrast Decorator with **inheritance** of combined policies. How does composition let you add or remove a policy without a new subclass for every combination?

With inheritance, every new policy combination could need another subclass. With Decorator, each policy is its own wrapper, so I can add or remove logging or max run-time by changing how the objects are composed instead of creating another actuator subclass.


### 10. A classmate’s decorator changes the method signature “a little” (extra required argument, different return type). Another ignores wrap order and cannot explain whether logging runs once per logical call or per inner attempt. Explain why each is a trap.

Changing the method signature breaks the main idea of Decorator because the wrapper should be usable anywhere the original component is expected. Ignoring wrapper order is also dangerous because order changes which behavior runs first and what gets recorded. The stack should be documented so we know exactly when logging and other policies run.