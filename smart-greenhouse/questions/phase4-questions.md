# Phase 4 — Builder questions

**Pattern / focus:** Builder.

## How to answer

- Use your own wording. Do not paste teaching-example types (for example ramen orders) as if they were your greenhouse classes.
- When a question asks about *this application*, refer to locations, zones, `location_id`, and the configuration wizard from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of Builder in plain language. Why does construction of a complex object need **stepwise assembly** and **validation at the end** (`build()`), instead of a telescoping constructor or a half-filled dict written straight to the database?

Builder creates a complex object step by step and checks that the final result is valid before it is used. In this project, a location needs a name and valid zones, so `build()` makes sure the configuration is complete before anything is saved. This is safer and easier to understand than using a very large constructor or saving incomplete data.

2. Name the main participants (**product**, **builder**, **optional director**, **client**). Until `build()` succeeds, is the intermediate object a finished domain product? Why does that distinction matter?

The product is the completed `LocationConfig`, the builder is `LocationConfigBuilder`, and the client is the application service that uses the builder. A director is optional and is not needed in my implementation. Before `build()` succeeds, the configuration is not a finished domain product because it may still be incomplete or invalid.

3. List at least three kinds of invalid configuration a location/zone `build()` should reject in **this** lab (name, zones, moisture thresholds). Why must those rules live in the **domain** builder, not only in the HTTP layer?

The builder should reject an empty location name, a location with no zones, duplicate zone names, thresholds outside `0.0–1.0`, and a low threshold that is equal to or higher than the high threshold. These rules belong in the domain so the same validation is used even if the configuration is created somewhere other than the HTTP API.

## B. This phase of the application

4. What aggregate does the builder produce (location plus zones)? Why does this course use **`location_id`** (and never `greenhouse_id`) as the name for that scope?

The builder produces a `LocationConfig` containing one location and its zones. The project uses `location_id` because zones and device assignments are scoped to a saved location. Using one consistent name also avoids mixing location configuration with the general smart greenhouse product name.

5. Describe the path from API request to persistence: DTO → builder steps → `build()` → repository. What must **not** be persisted if `build()` raises `ConfigurationError` (or equivalent)? Why does assigning a device wait until the zone row exists, and why does the client send only `zone_id`?

The API receives a DTO, the mapper passes its values to `LocationConfigBuilder`, `build()` validates the configuration, and only a valid result is sent to the repository. If `build()` raises `ConfigurationError`, no location or zone should be saved. Device assignment waits until the zone exists because it needs a real zone ID. The client only sends `zone_id`, and the backend gets the correct `location_id` from that zone.

6. Saving a location and its zones must be **one transaction**. What goes wrong if the location row commits and a later zone insert fails? How does that relate to “no half-built aggregates in the database”?

If the location is committed first and a zone insert later fails, the database could contain a location with missing zones. That would leave an incomplete configuration. Using one transaction means either the whole location and all zones are saved or everything is rolled back.

7. The configuration wizard UI collects fields in steps. How does that UI map to Builder without turning React (or the HTTP handler) into the place that owns domain validation?

The wizard collects the location name, zones, thresholds, and schedule from the user and sends them to the API. React can show simple input warnings, but the real domain validation still happens in `LocationConfigBuilder`. This keeps the business rules in one place.

## C. Compare, contrast, and scenarios

8. Contrast Builder with Factory Method and with Abstract Factory. Which pattern answers “which type?”, which answers “which matching kit?”, and which answers “how do we assemble one **valid whole** in steps?”

Factory Method answers **which type of object should be created**, such as a moisture or light sensor. Abstract Factory answers **which matching family of objects should be created**, such as a simulation or edge kit. Builder answers **how one complex and valid object should be assembled step by step**, such as a location with its zones.

9. Fluent method chaining (`builder.add_zone(...).build()`) is a coding style. Why is a fluent interface **not** the same thing as the Builder pattern?

A fluent interface only means methods can be chained together. Builder is a design pattern because it separates the step-by-step construction and final validation of a complex object. A class can use method chaining without actually being a Builder.

10. A classmate validates thresholds only in FastAPI / Pydantic and leaves `build()` empty. Another mutates builder fields after `build()` while treating the product as immutable. Explain why each is a trap.

If validation only exists in FastAPI or Pydantic, other parts of the application could create invalid domain configurations without using the API. `build()` should therefore enforce the important domain rules. Also, changing builder data after `build()` should not change an already created immutable product. The built configuration should stay stable and separate from later builder changes.