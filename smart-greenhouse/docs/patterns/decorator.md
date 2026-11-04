# Decorator Pattern

## Problem

The actuator adapter needs extra behavior such as logging and safety policies.

Putting all of these checks directly inside `SimulationActuatorAdapter` would make the adapter large and difficult to extend.

Using decorators allows extra behavior to be added around the actuator port without changing the original adapter.

## Solution

All actuator decorators implement the same `ActuatorPort` interface.

The Phase 9 decorator chain is:

```text
LoggingActuatorDecorator
        ↓
MaxRuntimeActuatorDecorator
        ↓
SimulationActuatorAdapter