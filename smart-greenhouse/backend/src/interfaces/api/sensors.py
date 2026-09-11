from typing import Generator
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.application.sensors.service import SensorService
from src.infrastructure.db import SessionLocal
from src.infrastructure.persistence.device_repository import DeviceRepository


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


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def get_service(db: Session = Depends(get_db)) -> SensorService:
    repository = DeviceRepository(db)
    return SensorService(repository)


@router.get("", response_model=list[SensorResponse])
def list_sensors(
    service: SensorService = Depends(get_service),
):
    return service.list_sensors()


@router.post(
    "",
    response_model=SensorResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_sensor(
    request: SensorCreateRequest,
    service: SensorService = Depends(get_service),
):
    try:
        return service.create_sensor(
            sensor_type=request.type,
            display_name=request.display_name,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error