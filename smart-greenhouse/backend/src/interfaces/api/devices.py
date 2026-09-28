from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from src.application.devices.dto import DeviceDto
from src.application.devices.family_service import DeviceFamilyService
from src.application.devices.mappers import (
    device_to_dto,
    devices_to_dto,
)
from src.application.locations.dto import (
    DeviceZoneAssignmentRequest,
)
from src.application.locations.zone_assignment_service import (
    ZoneAssignmentService,
)
from src.infrastructure.db import get_db
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
    family: str | None = Query(default=None),
    role: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[DeviceDto]:
    repository = DeviceRepository(db)
    service = DeviceFamilyService(repository)

    devices = service.list_devices(
        family=family,
        role=role,
    )

    return devices_to_dto(devices)


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
    service = DeviceFamilyService(repository)

    try:
        devices = service.provision_family(
            family
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return devices_to_dto(devices)


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
    service = ZoneAssignmentService(repository)

    try:
        device = service.assign(
            device_id=device_id,
            zone_id=request.zone_id,
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found",
        )

    return device_to_dto(device)