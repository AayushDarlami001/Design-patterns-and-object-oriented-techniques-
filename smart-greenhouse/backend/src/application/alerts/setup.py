from sqlalchemy.orm import Session

from src.application.alerts.subscribers import (
    AlertPersistenceSubscriber,
    MoistureThresholdSubscriber,
)
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


def build_event_bus(
    db: Session,
) -> EventBus:
    bus = EventBus()

    alert_repository = AlertRepository(db)

    moisture_subscriber = (
        MoistureThresholdSubscriber(
            db=db,
            event_bus=bus,
        )
    )

    alert_subscriber = (
        AlertPersistenceSubscriber(
            repository=alert_repository,
        )
    )

    # reading.created
    #     ↓
    # moisture threshold rule
    bus.subscribe(
        ReadingCreated,
        moisture_subscriber.handle,
    )

    # threshold.crossed
    #     ↓
    # persisted warning alert
    bus.subscribe(
        ThresholdCrossed,
        alert_subscriber.handle_threshold_crossed,
    )

    # command.failed
    #     ↓
    # persisted warning alert
    bus.subscribe(
        CommandFailed,
        alert_subscriber.handle_command_failed,
    )

    # state.changed
    #     ↓
    # persisted only when state == error
    bus.subscribe(
        ActuatorStateChanged,
        alert_subscriber.handle_state_changed,
    )

    return bus