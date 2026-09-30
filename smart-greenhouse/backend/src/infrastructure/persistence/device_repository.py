from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.domain.devices.entity import Device
from src.domain.sensors.entity import Sensor
from src.infrastructure.persistence.models import (
    DeviceRow,
    ZoneRow,
)


class DeviceRepository:
    def __init__(
        self,
        session: Session,
    ):
        self.session = session

    def add_sensor(
        self,
        sensor: Sensor,
    ) -> Sensor:
        interval = sensor.default_config.get(
            "sampling_interval_seconds",
            sensor.default_config.get(
                "sampling_interval",
                300,
            ),
        )

        config = {
            **sensor.default_config,
            "protocol": sensor.default_config.get(
                "protocol",
                "simulation",
            ),
        }

        row = DeviceRow(
            device_type=sensor.device_type,
            role="sensor",
            device_family="simulation",
            display_name=sensor.display_name,
            default_config=config,
            sampling_interval_seconds=int(interval),
            tracking_enabled=True,
        )

        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)

        return Sensor(
            id=row.id,
            device_type=row.device_type,
            display_name=row.display_name or "",
            default_config=row.default_config,
        )

    def list_sensors(
        self,
    ) -> list[Sensor]:
        statement = (
            select(DeviceRow)
            .where(
                DeviceRow.role == "sensor"
            )
            .order_by(
                DeviceRow.created_at.desc()
            )
        )

        rows = self.session.scalars(
            statement
        ).all()

        return [
            Sensor(
                id=row.id,
                device_type=row.device_type,
                display_name=row.display_name or "",
                default_config=row.default_config,
            )
            for row in rows
        ]

    def save_device(
        self,
        device: Device,
    ) -> Device:
        row = DeviceRow(
            device_type=device.device_type,
            role=device.role,
            device_family=device.device_family,
            display_name=device.display_name,
            default_config=device.default_config,
            zone_id=device.zone_id,
            location_id=device.location_id,
            sampling_interval_seconds=(
                device.sampling_interval_seconds
            ),
            tracking_enabled=(
                device.tracking_enabled
            ),
        )

        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)

        return self._row_to_device(row)

    def save_devices(
        self,
        devices: list[Device],
    ) -> list[Device]:
        rows = [
            DeviceRow(
                device_type=device.device_type,
                role=device.role,
                device_family=device.device_family,
                display_name=device.display_name,
                default_config=device.default_config,
                zone_id=device.zone_id,
                location_id=device.location_id,
                sampling_interval_seconds=(
                    device.sampling_interval_seconds
                ),
                tracking_enabled=(
                    device.tracking_enabled
                ),
            )
            for device in devices
        ]

        self.session.add_all(rows)
        self.session.commit()

        for row in rows:
            self.session.refresh(row)

        return [
            self._row_to_device(row)
            for row in rows
        ]

    def get_device(
        self,
        device_id: UUID,
    ) -> Device | None:
        row = self.session.get(
            DeviceRow,
            device_id,
        )

        if row is None:
            return None

        return self._row_to_device(row)

    def list_devices(
        self,
        device_family: str | None = None,
        role: str | None = None,
    ) -> list[Device]:
        statement = select(DeviceRow)

        if device_family is not None:
            statement = statement.where(
                DeviceRow.device_family
                == device_family
            )

        if role is not None:
            statement = statement.where(
                DeviceRow.role == role
            )

        statement = statement.order_by(
            DeviceRow.created_at.desc()
        )

        rows = self.session.scalars(
            statement
        ).all()

        return [
            self._row_to_device(row)
            for row in rows
        ]

    def list_tracked_simulation_sensors(
        self,
    ) -> list[Device]:
        statement = select(DeviceRow).where(
            DeviceRow.role == "sensor",
            DeviceRow.tracking_enabled.is_(True),
        )

        rows = self.session.scalars(
            statement
        ).all()

        return [
            self._row_to_device(row)
            for row in rows
            if row.default_config.get(
                "protocol",
                "simulation",
            )
            == "simulation"
        ]

    def update_sampling(
        self,
        device_id: UUID,
        sampling_interval_seconds: int,
        tracking_enabled: bool,
    ) -> Device | None:
        row = self.session.get(
            DeviceRow,
            device_id,
        )

        if row is None:
            return None

        row.sampling_interval_seconds = (
            sampling_interval_seconds
        )

        row.tracking_enabled = (
            tracking_enabled
        )

        self.session.commit()
        self.session.refresh(row)

        return self._row_to_device(row)

    def assign_device_to_zone(
        self,
        device_id: UUID,
        zone_id: UUID,
    ) -> Device | None:
        device = self.session.get(
            DeviceRow,
            device_id,
        )

        if device is None:
            return None

        zone = self.session.get(
            ZoneRow,
            zone_id,
        )

        if zone is None:
            raise LookupError(
                "Zone not found"
            )

        device.zone_id = zone.id
        device.location_id = zone.location_id

        self.session.commit()
        self.session.refresh(device)

        return self._row_to_device(
            device
        )

    def unassign_device(
        self,
        device_id: UUID,
    ) -> Device | None:
        device = self.session.get(
            DeviceRow,
            device_id,
        )

        if device is None:
            return None

        device.zone_id = None
        device.location_id = None

        self.session.commit()
        self.session.refresh(device)

        return self._row_to_device(
            device
        )

    def list_devices_in_zone(
        self,
        location_id: UUID,
        zone_id: UUID,
    ) -> list[Device] | None:
        zone = self.session.get(
            ZoneRow,
            zone_id,
        )

        if (
            zone is None
            or zone.location_id != location_id
        ):
            return None

        statement = (
            select(DeviceRow)
            .where(
                DeviceRow.zone_id == zone_id
            )
            .order_by(
                DeviceRow.created_at.desc()
            )
        )

        rows = self.session.scalars(
            statement
        ).all()

        return [
            self._row_to_device(row)
            for row in rows
        ]

    @staticmethod
    def _row_to_device(
        row: DeviceRow,
    ) -> Device:
        return Device(
            id=row.id,
            device_type=row.device_type,
            role=row.role,
            device_family=row.device_family,
            display_name=row.display_name or "",
            default_config=row.default_config,
            zone_id=row.zone_id,
            location_id=row.location_id,
            sampling_interval_seconds=(
                row.sampling_interval_seconds
            ),
            tracking_enabled=(
                row.tracking_enabled
            ),
        )