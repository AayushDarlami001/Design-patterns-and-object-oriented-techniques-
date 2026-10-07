# Phase 6 — Strategy questions

**Pattern / focus:** Strategy.

## A. Pattern

1. State the intent of Strategy in plain language. How does the **context** use a strategy, and why must “choose which algorithm” stay separate from “run the algorithm”?
>
> Strategy lets the application choose between different algorithms that share the same interface. The context gives the selected strategy the data it needs and calls `decide(context)`. Choosing which strategy to use should stay separate from running it so the algorithms can be changed without changing the evaluation workflow.

2. Name the participants (**strategy**, **concrete strategies**, **context**, **client**). What goes wrong when all policies live as `if/elif` inside the context (or inside an HTTP router)?
>
> The strategy is `AutomationStrategy`, and the concrete strategies are `ConservativeMoistureStrategy` and `AggressiveMoistureStrategy`. The context is `LocationAutomationContext`, and the application service is the client that selects and runs the strategy. If all policies are written as `if/elif` in the service or router, the code becomes tightly coupled and harder to extend or test.

3. When should you use Strategy, and when should you skip it (one algorithm only; or the variation is a **lifecycle mode** rather than a chosen policy
>
> Strategy is useful when there are several interchangeable algorithms and the application needs to choose between them. If there is only one algorithm and no real variation, Strategy may add unnecessary complexity. If the variation represents an object's lifecycle, such as changing between operating states, State is usually a better pattern.

## B. This phase of the application

4. In this lab, what does a strategy’s `decide(context)` return (action + reason)? Give a concrete difference you implemented (or were required to implement) between **conservative** and **aggressive** on the **same** moisture reading and zone thresholds.
>
> `decide(context)` returns a `Recommendation` with an action such as `irrigate` or `wait`, a reason, and optionally a score. In my implementation, with moisture `0.40`, low threshold `0.30`, and high threshold `0.50`, the conservative strategy returns `wait`, while the aggressive strategy returns `irrigate`.

5. Where do the numbers in `LocationAutomationContext` (or your equivalent) come from? Latest moisture may already be in `sensor_readings` from a manual read, the simulation sampler, or MQTT translation — why does this phase not add a scheduler or a broker? Why must strategies receive a plain context object, not SQLAlchemy rows or FastAPI types? Why are thresholds read from **zones**, not hardcoded in the strategy class?
>
> The context is built from the selected location's zones, their stored low and high moisture thresholds, and the latest moisture reading from a sensor assigned to that specific zone. The reading may already come from manual reading, simulation sampling, or MQTT translation, so Phase 6 does not need another scheduler or broker. Strategies receive plain Python data so the domain logic stays independent from SQLAlchemy and FastAPI. Thresholds come from each zone because different zones can have different settings and the algorithm should not contain hardcoded values.

6. The active `strategy_key` is **persisted** per `location_id` (for example in `automation_rules`). Why must `POST .../automation/evaluate` use the **saved** key rather than a key the client sends only in that request? What happens on the next evaluate after the operator changes strategy but moisture stays the same?

>
> The strategy key is persisted so the location has a clear active automation policy that remains the same between requests and page refreshes. The evaluate endpoint loads that saved key instead of trusting a temporary query value. If the operator changes from conservative to aggressive while the moisture remains the same, the next evaluation uses the newly saved strategy and can return a different recommendation.

7. Strategy **recommends** (irrigate / wait). It should not itself start a pump. Why keep **decide** separate from **execute**? Which later pattern is meant to carry out the action?
>
> `decide` should only contain the decision policy. Starting a pump is a separate side effect and mixing it into the Strategy would make the policy harder to test and reuse. The recommendation can later be passed to the Command pattern, which is responsible for representing and carrying out actions such as starting or stopping an actuator.

## C. Compare, contrast, and scenarios

8. Contrast Strategy with **State** (Phase 8). Both delegate to an object with the same shape. Who typically **changes** the active object, and is the variation a **policy** or a **lifecycle**?

>
> Strategy represents a chosen policy, and the client or operator usually selects which strategy should be active. State represents the current lifecycle condition of an object, and the object or state transitions usually change the active state. Strategy answers "which algorithm should we use?", while State answers "what state is the object currently in?"

9. Contrast Strategy with **Adapter** (Phase 5) and with **Builder** (Phase 4). Which one translates a foreign API, which one assembles a valid aggregate, and which one swaps an algorithm?

> Adapter translates an incompatible external format into the interface the application expects, such as turning vendor or MQTT sensor data into a normalized `Reading`. Builder creates a valid configuration step by step, such as a location with its zones. Strategy swaps between algorithms, such as conservative and aggressive irrigation policies.

10. A classmate writes one “mega-strategy” that still contains `if conservative` / `if aggressive` inside a single class. Another strategy class calls the actuator adapter to water immediately. Explain why each is a trap.

>
> A mega-strategy with `if conservative` and `if aggressive` defeats the purpose of Strategy because the algorithms are still coupled inside one class. Each policy should be its own implementation behind the common interface. Calling an actuator directly from the strategy is also a problem because it mixes decision logic with execution and hardware side effects. The strategy should only return a recommendation, and another layer or later pattern should execute it.