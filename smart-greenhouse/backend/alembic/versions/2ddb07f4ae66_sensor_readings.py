"""sensor readings

Revision ID: 2ddb07f4ae66
Revises: 0ad582abd737
Create Date: 2026-09-30 12:59:06.744829

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "2ddb07f4ae66"
down_revision: Union[str, Sequence[str], None] = "0ad582abd737"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sensor_readings",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "device_id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "value",
            sa.Numeric(precision=12, scale=4),
            nullable=False,
        ),
        sa.Column(
            "unit",
            sa.String(length=32),
            nullable=False,
        ),
        sa.Column(
            "source",
            sa.String(length=32),
            nullable=False,
        ),
        sa.Column(
            "recorded_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["device_id"],
            ["devices.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_sensor_readings_device_recorded_at",
        "sensor_readings",
        [
            "device_id",
            sa.literal_column("recorded_at DESC"),
        ],
        unique=False,
    )

    op.add_column(
        "devices",
        sa.Column(
            "sampling_interval_seconds",
            sa.Integer(),
            server_default=sa.text("300"),
            nullable=False,
        ),
    )

    op.add_column(
        "devices",
        sa.Column(
            "tracking_enabled",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
    )

    op.execute(
        """
        UPDATE devices
        SET sampling_interval_seconds =
            (default_config->>'sampling_interval_seconds')::integer
        WHERE default_config ? 'sampling_interval_seconds'
          AND jsonb_typeof(
              default_config->'sampling_interval_seconds'
          ) = 'number'
        """
    )


def downgrade() -> None:
    op.drop_column(
        "devices",
        "tracking_enabled",
    )

    op.drop_column(
        "devices",
        "sampling_interval_seconds",
    )

    op.drop_index(
        "ix_sensor_readings_device_recorded_at",
        table_name="sensor_readings",
    )

    op.drop_table(
        "sensor_readings",
    )