# Phase 8 — State questions

**Pattern / focus:** State.

## A. Pattern

### 1. State the intent of the State pattern in plain language. What problem appears when lifecycle is modelled as boolean flags and scattered `if` guards?

The State pattern keeps an object's behavior and legal transitions based on its current lifecycle state. If we use many boolean flags and scattered `if` checks, invalid combinations can appear and some code paths may forget to check the rules. State keeps those lifecycle rules in one clear place.


### 2. Name the participants (**context**, **state interface**, **concrete states**, **client**). How does a successful command lead to a **transition**, and where do **guards** live?

The context in my project is `ActuatorContext`. The State role is represented by the actuator state logic and transition table, while `idle`, `running`, `off`, `error`, and `maintenance` are the concrete lifecycle states. The API is the client. A requested transition is checked by the domain rules, and if it is legal the context changes state and the service saves it. The guards stay in the domain, not in the API or frontend.


### 3. What is `allowed_commands` (or equivalent) for? Why is exposing “what can I do **now**?” better than letting the UI guess from a raw state string?

`allowed_commands` tells the client which actions are legal in the current state. This is better than letting React guess because the backend domain is the source of truth. It also avoids duplicating transition rules in the frontend.


## B. This phase of the application

### 4. Which actuator states did you implement (for example idle, running, error)? Sketch the **legal** transitions (which command or event moves idle → running, running → idle, into error, and out of error).


I implemented `off`, `idle`, `running`, `error`, and `maintenance`. From `idle`, `start_pump` moves the actuator to `running`. From `running`, `stop_pump` moves it back to `idle`. A fault can move supported states into `error`, and `reset` moves `error` back to `idle`.


### 5. Why is actuator state stored in `actuator_states` (or equivalent) rather than only in process memory? What must still be true after you restart the backend?

The state is stored in `actuator_states` so it is not lost when the FastAPI process stops or restarts. After restarting the backend, each actuator must still have the same stored state and the correct `allowed_commands` must be calculated from it.


### 6. An **illegal** transition must raise a domain error and **must not** update the database. Why? Which HTTP status is reasonable for that case (400 or 409), and why should the rule live in the domain rather than in React?

An illegal transition must not be saved because it would put the actuator into a state that breaks the lifecycle rules. I use `409 Conflict` because the request conflicts with the actuator's current state. The rule belongs in the domain so every client follows the same rules instead of relying on React to enforce them.


### 7. Device JSON gains `state` and `allowed_commands`. How does the dashboard use those fields (badges, disable illegal buttons)? How does this prepare **Phase 10 Command**?

The dashboard shows the actuator's current state as a badge and uses `allowed_commands` to know which actions are currently legal. This means illegal actions can be hidden or disabled instead of guessed by the UI. It also prepares Phase 10 because the Command pattern can reuse the same command names and let State decide whether they are allowed.


## C. Compare, contrast, and scenarios

### 8. Contrast State with **Strategy**. Both look like “context delegates to an object.” Who typically **changes** the active object, and is the variation a **lifecycle** or a **selectable policy**? Give a greenhouse example of each (this phase vs Phase 6).

State changes because the object moves through its lifecycle. For example, an actuator can move from `idle` to `running` and later to `error`. Strategy is normally selected as a policy by the client or configuration. In Phase 6, the greenhouse could use a `conservative` or `aggressive` automation strategy, while Phase 8 changes actuator state as its lifecycle changes.


### 9. Contrast State with a pile of booleans (`is_running`, `is_fault`, `is_maintenance`). Why do illegal combinations of flags appear, and how do explicit state objects (or a transition table) prevent that?

With several booleans, more than one can accidentally be true at the same time, such as `is_running` and `is_maintenance`. This creates unclear or impossible situations. An explicit state or transition table gives the actuator one lifecycle state at a time and only allows transitions that are defined as legal.


### 10. A classmate puts HTTP status mapping or SQLAlchemy commits **inside** a concrete state class. Another state mutates a flag directly and skips `transition` / `set_state`. Explain why each is a trap.

Putting HTTP or SQLAlchemy code inside a state class mixes the domain with API and database concerns, making the design harder to test and maintain. Changing a flag directly is also a problem because it bypasses the transition guards. State changes should go through the domain transition logic first, and persistence should happen afterward in the application or repository layer.