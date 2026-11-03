from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from src.application.actuators.service import (
    ActuatorStateService,
)
from src.application.devices.dto import (
    DeviceDto,
    DeviceSamplingUpdateRequest,
)
from src.application.devices.family_service import (
    DeviceFamilyService,
)
from src.application.devices.mappers import (
    device_to_dto,
    devices_to_dto,
)
from src.application.devices.read_service import (
    DeviceReadService,
)
from src.application.locations.dto import (
    DeviceZoneAssignmentRequest,
)
from src.application.locations.zone_assignment_service import (
    ZoneAssignmentService,
)
from src.infrastructure.db import get_db
from src.infrastructure.persistence.actuator_state_repository import (
    ActuatorStateRepository,
)
from src.infrastructure.persistence.device_repository import (
    DeviceRepository,
)


router = APIRouter(
    prefix="/api/devices",
    tags=["devices"],
)


@router.get(
    "",
    response_model=list[DeviceDto],
)
def list_devices(
    family: str | None = Query(
        default=None
    ),
    role: str | None = Query(
        default=None
    ),
    db: Session = Depends(get_db),
) -> list[DeviceDto]:
    device_repository = (
        DeviceRepository(db)
    )

    actuator_state_repository = (
        ActuatorStateRepository(db)
    )

    actuator_state_service = (
        ActuatorStateService(
            actuator_state_repository
        )
    )

    read_service = DeviceReadService(
        device_repository=(
            device_repository
        ),
        actuator_state_service=(
            actuator_state_service
        ),
    )

    return read_service.list_devices(
        family=family,
        role=role,
    )


@router.post(
    "/provision",
    response_model=list[DeviceDto],
    status_code=status.HTTP_201_CREATED,
)
def provision_family(
    family: str = Query(...),
    db: Session = Depends(get_db),
) -> list[DeviceDto]:
    repository = DeviceRepository(db)
    service = DeviceFamilyService(
        repository
    )

    try:
        devices = service.provision_family(
            family
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            detail=str(exc),
        ) from exc

    return devices_to_dto(
        devices
    )


@router.patch(
    "/{device_id}/zone",
    response_model=DeviceDto,
)
def assign_device_zone(
    device_id: UUID,
    request: DeviceZoneAssignmentRequest,
    db: Session = Depends(get_db),
) -> DeviceDto:
    repository = DeviceRepository(db)
    service = ZoneAssignmentService(
        repository
    )

    try:
        device = service.assign(
            device_id=device_id,
            zone_id=request.zone_id,
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=str(exc),
        ) from exc

    if device is None:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail="Device not found",
        )

    return device_to_dto(
        device
    )


@router.patch(
    "/{device_id}/sampling",
    response_model=DeviceDto,
)
def update_sampling(
    device_id: UUID,
    request: DeviceSamplingUpdateRequest,
    db: Session = Depends(get_db),
) -> DeviceDto:
    if (
        request.sampling_interval_seconds
        < 5
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            detail=(
                "Sampling interval must be "
                "at least 5 seconds"
            ),
        )

    repository = DeviceRepository(db)

    device = repository.update_sampling(
        device_id=device_id,
        sampling_interval_seconds=(
            request.sampling_interval_seconds
        ),
        tracking_enabled=(
            request.tracking_enabled
        ),
    )

    if device is None:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail="Device not found",
        )

    return device_to_dto(
        device
    )