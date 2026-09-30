from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.application.readings.dto import ReadingDto
from src.application.readings.service import ReadingIngest
from src.application.sensors.service import SensorService
from src.infrastructure.db import get_db
from src.infrastructure.persistence.device_repository import (
    DeviceRepository,
)
from src.infrastructure.persistence.reading_repository import (
    ReadingRepository,
)


router = APIRouter(
    prefix="/api/sensors",
    tags=["Sensors"],
)


class SensorCreateRequest(BaseModel):
    type: str
    display_name: str | None = None


class SensorResponse(BaseModel):
    id: UUID
    device_type: str
    display_name: str
    default_config: dict


@router.get(
    "",
    response_model=list[SensorResponse],
)
def list_sensors(
    db: Session = Depends(get_db),
) -> list[SensorResponse]:
    repository = DeviceRepository(db)
    service = SensorService(repository)

    sensors = service.list_sensors()

    return [
        SensorResponse(
            id=sensor.id,
            device_type=sensor.device_type,
            display_name=sensor.display_name,
            default_config=sensor.default_config,
        )
        for sensor in sensors
        if sensor.id is not None
    ]


@router.post(
    "",
    response_model=SensorResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_sensor(
    request: SensorCreateRequest,
    db: Session = Depends(get_db),
) -> SensorResponse:
    repository = DeviceRepository(db)
    service = SensorService(repository)

    try:
        sensor = service.create_sensor(
            request.type,
            request.display_name,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    if sensor.id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sensor was not saved",
        )

    return SensorResponse(
        id=sensor.id,
        device_type=sensor.device_type,
        display_name=sensor.display_name,
        default_config=sensor.default_config,
    )


@router.post(
    "/{device_id}/read",
    response_model=ReadingDto,
    status_code=status.HTTP_201_CREATED,
)
def read_sensor(
    device_id: UUID,
    db: Session = Depends(get_db),
) -> ReadingDto:
    device_repository = DeviceRepository(db)
    reading_repository = ReadingRepository(db)

    service = ReadingIngest(
        device_repository=device_repository,
        reading_repository=reading_repository,
    )

    try:
        return service.record(device_id)

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "/{device_id}/readings",
    response_model=list[ReadingDto],
)
def list_sensor_readings(
    device_id: UUID,
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
) -> list[ReadingDto]:
    device_repository = DeviceRepository(db)
    reading_repository = ReadingRepository(db)

    service = ReadingIngest(
        device_repository=device_repository,
        reading_repository=reading_repository,
    )

    try:
        return service.list_recent(
            device_id=device_id,
            limit=limit,
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc