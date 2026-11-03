"""add actuator states

Revision ID: 17389f20acb4
Revises: 073cb6dca9df
Create Date: 2026-11-03 18:28:50.621078
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "17389f20acb4"
down_revision: Union[str, Sequence[str], None] = "073cb6dca9df"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "actuator_states",
        sa.Column(
            "device_id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "state",
            sa.String(length=32),
            server_default=sa.text("'idle'"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["device_id"],
            ["devices.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "device_id"
        ),
    )

    # Seed all existing actuator devices with the default state "idle".
    op.execute(
        """
        INSERT INTO actuator_states (
            device_id,
            state
        )
        SELECT
            id,
            'idle'
        FROM devices
        WHERE role = 'actuator'
        ON CONFLICT (device_id) DO NOTHING
        """
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_table(
        "actuator_states"
    )