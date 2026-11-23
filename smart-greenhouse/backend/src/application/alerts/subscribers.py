from sqlalchemy.orm import Session

from src.domain.events.bus import EventBus
from src.domain.events.events import (
    ActuatorStateChanged,
    CommandFailed,
    ReadingCreated,
    ThresholdCrossed,
)
from src.infrastructure.persistence.alert_repository import (
    AlertRepository,
)
from src.infrastructure.persistence.models import (
    ZoneRow,
)


class MoistureThresholdSubscriber:
    def __init__(
        self,
        db: Session,
        event_bus: EventBus,
    ):
        self.db = db
        self.event_bus = event_bus

    def handle(
        self,
        event: ReadingCreated,
    ) -> None:
        # Only moisture/VWC readings
        # participate in this rule.
        if event.unit.lower() != "vwc":
            return

        # Unassigned devices must not invent
        # a zone.
        if event.zone_id is None:
            return

        zone = self.db.get(
            ZoneRow,
            event.zone_id,
        )

        if zone is None:
            return

        threshold_low = float(
            zone.moisture_threshold_low
        )

        # The assignment requires strictly
        # below the low threshold.
        if event.value >= threshold_low:
            return

        self.event_bus.publish(
            ThresholdCrossed(
                device_id=event.device_id,
                location_id=event.location_id,
                zone_id=event.zone_id,
                value=event.value,
                threshold_low=threshold_low,
            )
        )


class AlertPersistenceSubscriber:
    def __init__(
        self,
        repository: AlertRepository,
    ):
        self.repository = repository

    def handle_threshold_crossed(
        self,
        event: ThresholdCrossed,
    ) -> None:
        self.repository.create(
            location_id=event.location_id,
            zone_id=event.zone_id,
            device_id=event.device_id,
            severity="warning",
            message=(
                "Moisture below zone low"
            ),
            event_type="threshold.crossed",
            status="active",
        )

    def handle_command_failed(
        self,
        event: CommandFailed,
    ) -> None:
        self.repository.create(
            location_id=event.location_id,
            zone_id=event.zone_id,
            device_id=event.device_id,
            severity="warning",
            message=event.error_message,
            event_type="command.failed",
            status="active",
        )

    def handle_state_changed(
        self,
        event: ActuatorStateChanged,
    ) -> None:
        # Only entering the error state
        # creates an alert.
        if event.state != "error":
            return

        self.repository.create(
            location_id=event.location_id,
            zone_id=event.zone_id,
            device_id=event.device_id,
            severity="critical",
            message=(
                "Actuator entered error"
            ),
            event_type="state.changed",
            status="active",
        )