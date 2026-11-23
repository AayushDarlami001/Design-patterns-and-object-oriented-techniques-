from sqlalchemy.orm import Session

from src.application.alerts.setup import build_event_bus
from src.application.commands.dto import (
    CommandLogDto,
    CommandRequest,
)
from src.domain.actuators.context import (
    ActuatorContext,
)
from src.domain.commands.invoker import (
    CommandInvoker,
)
from src.domain.events.events import (
    ActuatorStateChanged,
    CommandFailed,
)
from src.infrastructure.adapters.actuators.factory import (
    build_actuator_port,
)
from src.infrastructure.persistence.actuator_state_repository import (
    ActuatorStateRepository,
)
from src.infrastructure.persistence.command_log_repository import (
    CommandLogRepository,
)
from src.infrastructure.persistence.models import (
    CommandLogRow,
)


class DeviceNotFoundError(LookupError):
    pass


def command_log_to_dto(
    row: CommandLogRow,
) -> CommandLogDto:
    return CommandLogDto(
        id=row.id,
        command_type=row.command_type,
        device_id=row.device_id,
        payload=row.payload,
        status=row.status,
        error_message=row.error_message,
        created_at=row.created_at,
    )


class CommandService:
    def __init__(
        self,
        db: Session,
    ):
        self.state_repository = (
            ActuatorStateRepository(db)
        )

        self.command_log_repository = (
            CommandLogRepository(db)
        )

        self.invoker = CommandInvoker()

        self.actuator_port = (
            build_actuator_port(db)
        )

        # Phase 11 — Observer
        self.event_bus = build_event_bus(db)

    def execute(
        self,
        request: CommandRequest,
    ) -> CommandLogDto:
        actuator = (
            self.state_repository.get_actuator(
                request.device_id
            )
        )

        if actuator is None:
            raise DeviceNotFoundError(
                "Actuator not found"
            )

        # Unknown commands are checked before
        # command_log is written.
        command = self.invoker.create(
            request.command_type,
            request.device_id,
            request.payload,
        )

        state_row = (
            self.state_repository.get_state(
                request.device_id
            )
        )

        current_state = (
            state_row.state
            if state_row is not None
            else "idle"
        )

        context = ActuatorContext(
            device_id=request.device_id,
            state=current_state,
        )

        # Illegal commands are rejected.
        # They do not call the actuator port
        # and do not change actuator state.
        if (
            request.command_type
            not in context.allowed_commands
        ):
            row = (
                self.command_log_repository.create(
                    command_type=(
                        request.command_type
                    ),
                    device_id=(
                        request.device_id
                    ),
                    payload=request.payload,
                    status="rejected",
                    error_message=(
                        f"Command "
                        f"'{request.command_type}' "
                        f"is not allowed while "
                        f"actuator is "
                        f"'{context.state}'"
                    ),
                )
            )

            return command_log_to_dto(row)

        try:
            # Phase 10 — Command pattern
            self.invoker.execute(
                command=command,
                port=self.actuator_port,
            )

            # State update happens only after
            # successful command execution.
            if (
                command.target_state
                is not None
                and command.target_state
                != context.state
            ):
                previous_state = (
                    context.state
                )

                context.transition_to(
                    command.target_state
                )

                self.state_repository.save_state(
                    device_id=(
                        request.device_id
                    ),
                    state=context.state,
                )

                # Phase 11 — Observer
                #
                # Publish state.changed only
                # after the new state has been
                # successfully persisted.
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

        except Exception as exc:
            error_message = str(exc)

            row = (
                self.command_log_repository.create(
                    command_type=(
                        request.command_type
                    ),
                    device_id=(
                        request.device_id
                    ),
                    payload=request.payload,
                    status="failed",
                    error_message=(
                        error_message
                    ),
                )
            )

            # Phase 11 — Observer
            #
            # Actual execution failures publish
            # command.failed.
            #
            # Rejected commands do NOT publish
            # CommandFailed.
            self.event_bus.publish(
                CommandFailed(
                    device_id=actuator.id,
                    location_id=(
                        actuator.location_id
                    ),
                    zone_id=(
                        actuator.zone_id
                    ),
                    command_type=(
                        request.command_type
                    ),
                    error_message=(
                        error_message
                    ),
                )
            )

            return command_log_to_dto(row)

        row = (
            self.command_log_repository.create(
                command_type=(
                    request.command_type
                ),
                device_id=request.device_id,
                payload=request.payload,
                status="success",
                error_message=None,
            )
        )

        return command_log_to_dto(row)

    def list_recent(
        self,
        limit: int = 50,
    ) -> list[CommandLogDto]:
        rows = (
            self.command_log_repository.list_recent(
                limit=limit
            )
        )

        return [
            command_log_to_dto(row)
            for row in rows
        ]