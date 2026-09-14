"""add sensor_devices and sensor_observations tables

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-23
"""

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        "sensor_devices",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("field_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("transport_type", sa.String(50), nullable=False),
        sa.Column("device_id", sa.String(200), nullable=False),
        sa.Column("is_simulated", sa.Boolean(), default=False, nullable=False),
        sa.Column("is_stale", sa.Boolean(), default=False, nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("device_id"),
        sa.ForeignKeyConstraint(
            ["field_id"],
            ["fields.id"],
            ondelete="CASCADE",
        ),
    )
    op.create_index(
        "ix_sensor_devices_field_id",
        "sensor_devices",
        ["field_id"],
    )

    op.create_table(
        "sensor_observations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("device_id", sa.Integer(), nullable=False),
        sa.Column("event_id", sa.String(200), nullable=False),
        sa.Column("temperature", sa.Float(), nullable=True),
        sa.Column("humidity", sa.Float(), nullable=True),
        sa.Column("soil_moisture", sa.Float(), nullable=True),
        sa.Column("ph", sa.Float(), nullable=True),
        sa.Column("light", sa.Float(), nullable=True),
        sa.Column(
            "recorded_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("event_id"),
        sa.ForeignKeyConstraint(
            ["device_id"],
            ["sensor_devices.id"],
            ondelete="CASCADE",
        ),
    )
    op.create_index(
        "ix_sensor_observations_device_id",
        "sensor_observations",
        ["device_id"],
    )


def downgrade() -> None:
    op.drop_table("sensor_observations")
    op.drop_table("sensor_devices")
