# Command Pattern

## Intent

The Command pattern turns an action into an object.

In this project, actuator actions such as `start_pump`, `stop_pump`, and `set_light_level` are represented by command objects instead of being handled directly in the HTTP router.

Each command knows how to execute itself through `ActuatorPort`.

## Main participants

The common command abstraction is `Command`.

Concrete commands include:

- `StartPumpCommand`
- `StopPumpCommand`
- `SetLightLevelCommand`

The `CommandInvoker` receives a command type, looks it up from the command registry, creates the correct command object, and executes it.

The invoker does not use a long `if/elif` chain for every command type.

## Execution flow

The Phase 10 flow is:

```text
HTTP request
    ↓
CommandService
    ↓
CommandInvoker
    ↓
Concrete Command
    ↓
ActuatorPort
    ↓
LoggingActuatorDecorator
    ↓
MaxRuntimeActuatorDecorator
    ↓
SimulationActuatorAdapter
```

The router does not call the actuator adapter directly.

## Integration with State

Before a command is executed, the application service reads the persisted actuator state from Phase 8.

The requested command is checked against `allowed_commands`.

If the command is not allowed in the current state, it is rejected before the actuator port is called.

For example:

```text
state = idle
command = stop_pump
```

produces a `rejected` command log entry and leaves the actuator state unchanged.

A successful `start_pump` changes:

```text
idle → running
```

A successful `stop_pump` changes:

```text
running → idle
```

`set_light_level` can execute while the actuator remains in the same lifecycle state.

## Integration with Decorator

Commands execute through the Phase 9 decorated actuator port.

The order is:

```text
Logging
→ MaxRuntime
→ SimulationActuatorAdapter
```

If the max-run-time policy blocks the actuator call, the Phase 9 execution log records the policy failure.

Phase 10 also records the command as:

```text
status = failed
```

with the same error message.

## Command history

Every known command attempt is persisted in:

```text
command_log
```

The table stores:

- command ID
- command type
- device ID
- payload
- status
- error message
- creation time

The possible statuses are:

```text
success
failed
rejected
```

Unknown command types are different: they return an error and do not create a `command_log` row.

## Why use an invoker?

The invoker separates the caller from the concrete command classes.

The HTTP layer only needs to submit a command request to the application service.

The application service and invoker decide which command object to create and execute.

This keeps the router small and makes it easier to add more commands later.

## Command vs calling ActuatorPort directly

Calling `ActuatorPort` directly from the router would tightly couple the HTTP layer to actuator execution.

It would also make it easier to accidentally bypass:

- state validation
- command history
- decorator policies
- future command-related behavior

Using Command keeps these responsibilities in the correct layers and gives every actuator action a consistent execution path.

## Frontend

The dashboard uses `allowed_commands` to decide which controls are enabled.

For example:

```text
idle
→ Start Pump enabled
→ Stop Pump disabled
```

and:

```text
running
→ Start Pump disabled
→ Stop Pump enabled
→ Set Light Level enabled
```

After a command is executed, the frontend reloads the actuator state and command history.