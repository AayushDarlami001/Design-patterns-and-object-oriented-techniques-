from uuid import UUID

from src.domain.actuators.context import ActuatorContext
from src.domain.events.bus import EventBus
from src.domain.events.events import ActuatorStateChanged
from src.infrastructure.persistence.actuator_state_repository import (
    ActuatorStateRepository,
)


class ActuatorStateService:
    def __init__(
        self,
        repository: ActuatorStateRepository,
        event_bus: EventBus | None = None,
    ):
        self.repository = repository
        self.event_bus = event_bus

    def get_context(
        self,
        device_id: UUID,
    ) -> ActuatorContext:
        actuator = self.repository.get_actuator(
            device_id
        )

        if actuator is None:
            raise LookupError(
                "Actuator not found"
            )

        state_row = self.repository.get_state(
            device_id
        )

        if state_row is None:
            state_row = self.repository.save_state(
                device_id=device_id,
                state="idle",
            )

        return ActuatorContext(
            device_id=device_id,
            state=state_row.state,
        )

    def get_state(
        self,
        device_id: UUID,
    ) -> ActuatorContext:
        return self.get_context(
            device_id
        )

    def transition(
        self,
        device_id: UUID,
        target_state: str,
    ) -> ActuatorContext:
        actuator = self.repository.get_actuator(
            device_id
        )

        if actuator is None:
            raise LookupError(
                "Actuator not found"
            )

        context = self.get_context(
            device_id
        )

        previous_state = context.state

        # Phase 8 — State pattern validation.
        # Illegal transitions raise before
        # anything is saved.
        context.transition_to(
            target_state
        )

        # Persist only after a legal
        # transition succeeds.
        self.repository.save_state(
            device_id=device_id,
            state=context.state,
        )

        # Phase 11 — Observer
        #
        # Publish only after the state has
        # successfully been saved.
        if self.event_bus is not None:
            self.event_bus.publish(
                ActuatorStateChanged(
                    device_id=actuator.id,
                    location_id=(
                        actuator.location_id
                    ),
                    zone_id=(
                        actuator.zone_id
                    ),
                    previous_state=(
                        previous_state
                    ),
                    state=context.state,
                )
            )

        return context


# Phase 11 requirement naming.
#
# Existing Phase 8 code can continue importing
# ActuatorStateService, while Phase 11 can refer
# to the transition publisher by this name.
ActuatorTransitionService = (
   ActuatorStateService
)