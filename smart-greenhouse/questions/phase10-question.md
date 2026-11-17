# Phase 10 — Command questions

## A. Pattern

### 1. State the intent of Command in plain language. What does it mean to **objectify a request**, and what can you do with that object that you cannot do with a bare `actuator.start()` call (queue, audit, undo, history)?

Command turns an action request into an object instead of making a direct method call. Because the request is now an object, it can be stored, queued, logged in history, retried, or optionally undone. A direct `actuator.start()` call performs the action but does not leave a reusable request object behind.


### 2. Name the participants (**command**, **receiver**, **invoker**, **client**). Who creates the command, who triggers `execute()`, and who actually changes actuator/hardware state?

The command is an object such as `StartPumpCommand`. The client is the API/application side that creates the command, the `CommandInvoker` triggers its `execute()` method, and the receiver is the actuator context or `ActuatorPort` that performs the actual work and changes the hardware or state.


### 3. If a command supports undo, when must it capture the data needed to reverse the action? Why is “capture **before** mutate” critical?

The command must save the previous value before changing it. If it captures the value after the mutation, the original state may already be lost, so undo would not know what to restore. For example, a brightness command would need to remember the old level before setting the new one.


## B. This phase of the application

### 4. Which command types did you implement (for example `start_pump`, `stop_pump`, `set_light_level`)? Why does the HTTP handler create a command and pass it to an **invoker** (or application service) instead of calling the actuator adapter from the router?

I implemented `start_pump`, `stop_pump`, and `set_light_level`. The HTTP layer sends the request through the command service and `CommandInvoker` instead of calling the actuator adapter directly. This keeps the router simple and ensures commands always go through state checking, decorators, and command logging.


### 5. Walk through the execute path: (1) consult State / `allowed_commands`, (2) if illegal → **rejected**, (3) if legal → decorated `apply`, update `actuator_states`, log **success** or **failed**. Why must a rejected command **not** change actuator state and **not** reach inner `apply`?

First the service reads the current actuator state and checks `allowed_commands`. If the command is illegal, it writes a `rejected` row and stops without calling `apply` or updating the state. If it is legal, the command runs through the Phase 9 decorated port, then the state is updated if needed and the result is logged as `success` or `failed`. A rejected command must stop early because it was never valid for the current lifecycle state.


### 6. Distinguish **`rejected`** vs **`failed`** vs **`success`** in `command_log`. Give one greenhouse example of each. Why is “illegal in this state” not the same as “policy or adapter error after the command was accepted”?

`rejected` means the command was not legal in the current State, for example `stop_pump` while the pump is already `idle`. `failed` means the command was accepted but later failed, such as the max-run-time policy blocking execution. `success` means the command completed, for example `start_pump` changing the pump from `idle` to `running`. These are different because rejection happens before execution, while failure happens after the command has been accepted for execution.


### 7. Why is `command_log` a **different** table from Phase 9 `actuator_execution_log`? What concern does each log record (operator intent vs policy/adapter attempt)?

`command_log` records the command request and its final result, so it represents operator intent such as starting or stopping a pump. `actuator_execution_log` records what happened inside the decorated actuator execution, including policies such as logging or max run time. Keeping them separate lets us audit both the requested action and the lower-level execution attempt.


## C. Compare, contrast, and scenarios

### 8. Contrast Command with **Strategy**. Strategy is an interchangeable **algorithm** (decide / quote). Command is a **side-effectful request** with history. How do they cooperate in this app (Phase 6 recommends; Phase 10 executes)?

Strategy represents an interchangeable algorithm for deciding what should happen, while Command represents a request to actually perform an action. In this application, Phase 6 Strategy can recommend an irrigation action, and Phase 10 Command can execute that action and keep an audit history.


### 9. Contrast Command with **State**. Who **triggers** the action, and who **decides whether it is legal**? Why must commands not bypass state guards?


Command represents and triggers the requested action, while State decides whether that action is currently legal. For example, `StartPumpCommand` requests a start, but the State rules decide whether `start_pump` is allowed. Commands must not bypass State because that could allow invalid transitions and make the persisted lifecycle inconsistent.


### 10. The controls UI should disable actions that are not in `allowed_commands`. Why must the **backend** still reject illegal commands even if the UI is correct? What happens if a classmate’s command calls the raw adapter and skips State and Decorator?

The backend must still validate commands because requests can come from places other than the UI, such as direct API calls or another client. UI disabling is only a convenience, not a security or business-rule guarantee. If a command calls the raw adapter directly, it can bypass State validation, decorator policies, and execution logging, which breaks the required application flow.