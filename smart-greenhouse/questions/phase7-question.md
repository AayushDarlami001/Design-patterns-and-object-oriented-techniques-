# Phase 7 — Facade questions

## A. Pattern

1. State the intent of Facade in plain language. What problem appears when every HTTP handler (or every UI screen) repeats the same multi-step dance across repositories and services?

Facade provides one simple entry point to a more complicated group of services or repositories. If every route or UI screen repeats the same calls to locations, devices, readings, and automation, the code becomes duplicated and harder to maintain. A facade keeps that coordination in one place.

2. A facade **orchestrates** collaborators. What should it **not** become (a god object that owns all domain logic)? Where should irrigation policy, sensor translation, and persistence stay instead?

A facade should coordinate existing parts of the system, not contain all business logic itself. Irrigation policy should stay in the Strategy classes from Phase 6, sensor translation should stay in the Adapter classes from Phase 5, and database queries should stay in repositories. The facade only combines their results into one overview.

3. When should you use Facade, and when should you skip it (a single repository call is enough; or you actually need to **translate** a mismatched interface)?

Facade is useful when one operation needs several subsystems and the caller should not know all the steps. If one repository call already gives the needed result, a facade may be unnecessary. If the problem is converting an incompatible external interface into the application's expected format, Adapter is the better pattern.

## B. This phase of the application

4. What does `GET /api/locations/{location_id}/overview` return? Name the main pieces of the overview DTO: location, assigned device counts, and `zones` (thresholds, assigned devices, and those devices’ latest readings, including `tracking_enabled` and `sampling_interval_seconds`), plus strategy key and last recommendation. Why may those reading rows come from the sampler or MQTT ingest, not only from `POST /read`? Why is overview scoped by `location_id`?

The endpoint returns one `LocationOverviewDto` containing the location, assigned sensor and actuator counts, every zone, zone thresholds, assigned devices, and the latest reading for each device when available. Each reading summary also includes `tracking_enabled` and `sampling_interval_seconds`. It also returns the saved `strategy_key` and the last recommendation. Readings can come from manual reads, the simulation sampler, or MQTT ingest because all of them use the same persisted reading history. The overview is scoped by `location_id` because the dashboard shows one location and its zones and assigned devices. :chatgpt-content-reference{index="1"}

5. Why does this phase **not** require a new business table? What already exists from Phases 2–6 that the facade only **composes**?

A new table is not needed because the required information already exists. Locations and zones come from Phase 4, devices already exist from earlier phases, readings are stored in `sensor_readings` from Phase 5, and the saved strategy is stored in `automation_rules` from Phase 6. The facade only reads and combines this existing data. :chatgpt-content-reference{index="2"}

6. The overview HTTP handler should call **only** the facade, not reading/strategy/device repositories directly. Why? How does that help tests and later changes to the query shape?

The router should stay simple and only handle HTTP concerns. The facade owns the coordination between repositories and services, so the route does not become tightly coupled to database details. This makes testing easier because the overview behavior can be tested through one entry point, and the repository query strategy can change later without rewriting the HTTP handler. :chatgpt-content-reference{index="3"}

7. The location selector may use the existing locations list. The Overview cards come from **one** overview fetch, and Refresh repeats that same fetch. Why must the React page not stitch device, reading, and automation calls together to build the same snapshot? How does a new reading or a saved strategy show up on overview without extra frontend glue?

React should receive one ready-made overview DTO instead of duplicating backend coordination logic. If the frontend separately loads devices, readings, and automation, it becomes more complex and the responses could represent different moments in time. When a new reading is stored or the strategy changes, the next overview request reads the latest database state, so Refresh automatically shows the updated information without extra frontend merging code. :chatgpt-content-reference{index="4"}

## C. Compare, contrast, and scenarios

8. Contrast Facade with **Adapter**. One makes an existing interface usable; the other makes a subsystem simpler to call. Which is which, and how do both appear in this greenhouse app (Phase 5 vs Phase 7)?

Adapter changes an incompatible interface into the form the application expects. In Phase 5, sensor adapters convert simulation, vendor, or MQTT data into a common `Reading`. Facade does not translate those formats; it gives the caller one simple way to use several existing subsystems. In Phase 7, `LocationOverviewFacade` combines locations, devices, readings, and automation into one overview response.

9. This phase mentions **N+1** queries. What is an N+1 problem in an overview that lists latest readings for many devices, and what can the facade (or its repository) do about it without putting SQL in the router?

An N+1 problem happens when the application first loads a list of devices and then runs another database query for every device to get its latest reading. With many devices, this creates many unnecessary queries. The repository can instead load all assigned devices in one query and fetch the newest readings for all those device IDs in another query. The router still stays free of SQL. :chatgpt-content-reference{index="5"}

10. A classmate hides every error behind a generic “overview failed,” so a missing location, a DB outage, and a strategy error look the same. Why is that a trap for a facade?

A facade simplifies access to subsystems, but it should not remove useful error meaning. A missing location should still be handled as a not-found case, while other failures should remain distinguishable so they can be diagnosed correctly. If every problem becomes the same generic error, the API and developer lose information about what actually failed.