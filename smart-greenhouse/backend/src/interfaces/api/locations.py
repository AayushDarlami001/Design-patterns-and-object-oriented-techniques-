from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)
from sqlalchemy.orm import Session

from src.application.devices.dto import DeviceDto
from src.application.devices.mappers import (
    devices_to_dto,
)
from src.application.locations.config_service import (
    LocationConfigService,
)
from src.application.locations.dto import (
    LocationConfigCreateRequest,
    LocationConfigResponse,
    LocationListItemDto,
    ZoneCreateDto,
    ZoneDto,
    ZoneUpdateDto,
)
from src.application.locations.zone_assignment_service import (
    ZoneAssignmentService,
)
from src.domain.locations.errors import (
    ConfigurationError,
)
from src.infrastructure.db import get_db
from src.infrastructure.persistence.device_repository import (
    DeviceRepository,
)
from src.infrastructure.persistence.location_repository import (
    LocationRepository,
)


router = APIRouter(
    prefix="/api/locations",
    tags=["locations"],
)


# -------------------------------------------------
# List locations
# -------------------------------------------------

@router.get(
    "",
    response_model=list[LocationListItemDto],
)
def list_locations(
    db: Session = Depends(get_db),
) -> list[LocationListItemDto]:
    repository = LocationRepository(db)
    service = LocationConfigService(repository)

    return service.list_locations()


# -------------------------------------------------
# Create location configuration
# -------------------------------------------------

@router.post(
    "/config",
    response_model=LocationConfigResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_location_config(
    request: LocationConfigCreateRequest,
    db: Session = Depends(get_db),
) -> LocationConfigResponse:
    repository = LocationRepository(db)
    service = LocationConfigService(repository)

    try:
        return service.create_config(
            request
        )

    except ConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# -------------------------------------------------
# Get location configuration
# -------------------------------------------------

@router.get(
    "/{location_id}/config",
    response_model=LocationConfigResponse,
)
def get_location_config(
    location_id: UUID,
    db: Session = Depends(get_db),
) -> LocationConfigResponse:
    repository = LocationRepository(db)
    service = LocationConfigService(repository)

    result = service.get_config(
        location_id
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found",
        )

    return result


# -------------------------------------------------
# Delete location
# -------------------------------------------------

@router.delete(
    "/{location_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_location(
    location_id: UUID,
    db: Session = Depends(get_db),
) -> Response:
    repository = LocationRepository(db)
    service = LocationConfigService(repository)

    deleted = service.delete_location(
        location_id
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found",
        )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )


# -------------------------------------------------
# Add zone to existing location
# -------------------------------------------------

@router.post(
    "/{location_id}/zones",
    response_model=ZoneDto,
    status_code=status.HTTP_201_CREATED,
)
def add_zone(
    location_id: UUID,
    request: ZoneCreateDto,
    db: Session = Depends(get_db),
) -> ZoneDto:
    repository = LocationRepository(db)
    service = LocationConfigService(repository)

    try:
        zone = service.add_zone(
            location_id,
            request,
        )

    except ConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    if zone is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found",
        )

    return zone


# -------------------------------------------------
# Update existing zone
# -------------------------------------------------

@router.patch(
    "/{location_id}/zones/{zone_id}",
    response_model=ZoneDto,
)
def update_zone(
    location_id: UUID,
    zone_id: UUID,
    request: ZoneUpdateDto,
    db: Session = Depends(get_db),
) -> ZoneDto:
    repository = LocationRepository(db)
    service = LocationConfigService(repository)

    try:
        zone = service.update_zone(
            location_id,
            zone_id,
            request,
        )

    except ConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    if zone is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Zone not found in this location",
        )

    return zone


# -------------------------------------------------
# Delete zone
# -------------------------------------------------

@router.delete(
    "/{location_id}/zones/{zone_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_zone(
    location_id: UUID,
    zone_id: UUID,
    db: Session = Depends(get_db),
) -> Response:
    repository = LocationRepository(db)
    service = LocationConfigService(repository)

    try:
        deleted = service.delete_zone(
            location_id,
            zone_id,
        )

    except ConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Zone not found in this location",
        )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )


# -------------------------------------------------
# List devices assigned to a zone
# -------------------------------------------------

@router.get(
    "/{location_id}/zones/{zone_id}/devices",
    response_model=list[DeviceDto],
)
def list_zone_devices(
    location_id: UUID,
    zone_id: UUID,
    db: Session = Depends(get_db),
) -> list[DeviceDto]:
    repository = DeviceRepository(db)
    service = ZoneAssignmentService(repository)

    devices = service.list_zone_devices(
        location_id=location_id,
        zone_id=zone_id,
    )

    if devices is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Zone not found in this location",
        )

    return devices_to_dto(devices)