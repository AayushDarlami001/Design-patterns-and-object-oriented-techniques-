from sqlalchemy.orm import Session

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

        # Phase 9 decorator chain:
        # Logging -> MaxRuntime -> Simulation
        self.actuator_port = (
            build_actuator_port(db)
        )

    def execute(
        self,
        request: CommandRequest,
    ) -> CommandLogDto:
        # 1. Device must exist and must
        # have role="actuator".
        actuator = (
            self.state_repository.get_actuator(
                request.device_id
            )
        )

        if actuator is None:
            raise DeviceNotFoundError(
                "Actuator not found"
            )

        # 2. Unknown command types are
        # rejected before command_log is written.
        command = self.invoker.create(
            command_type=(
                request.command_type
            ),
            device_id=request.device_id,
            payload=request.payload,
        )

        # Read Phase 8 persisted state.
        #
        # If an actuator somehow does not yet
        # have a row, treat it as idle here.
        # Do not write a state row until a
        # successful command needs a state
        # transition.
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

        # 3. State guard.
        #
        # Rejected commands never reach the
        # actuator port and never update state.
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
            # 4. Execute through the Command
            # invoker and Phase 9 decorators.
            self.invoker.execute(
                command=command,
                port=self.actuator_port,
            )

            # 5. Only change Phase 8 state
            # after the actuator call succeeds.
            #
            # set_light_level has target_state
            # None, so it does not rewrite the
            # lifecycle state.
            if (
                command.target_state
                is not None
                and command.target_state
                != context.state
            ):
                context.transition_to(
                    command.target_state
                )

                self.state_repository.save_state(
                    device_id=(
                        request.device_id
                    ),
                    state=context.state,
                )

        except Exception as exc:
            # MaxRuntime and other execution
            # failures become command_log
            # status="failed".
            #
            # The Phase 9 logging decorator
            # has already written the related
            # actuator_execution_log row.
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
                    error_message=str(exc),
                )
            )

            return command_log_to_dto(row)

        # Successful apply and any required
        # state transition are complete.
        row = self.command_log_repository.create(
            command_type=(
                request.command_type
            ),
            device_id=request.device_id,
            payload=request.payload,
            status="success",
            error_message=None,
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