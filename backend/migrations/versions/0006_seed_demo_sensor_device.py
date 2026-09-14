"""seed the sensor device used by the frontend demo

Revision ID: 0006
Revises: 0005
Create Date: 2026-07-23
"""

from alembic import op

revision: str = "0006"
down_revision: str | None = "0005"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO sensor_devices
            (field_id, name, transport_type, device_id, is_simulated, is_stale)
        SELECT
            1,
            'Demo Wokwi Device',
            'wokwi',
            'wokwi-demo-device',
            TRUE,
            FALSE
        WHERE EXISTS (SELECT 1 FROM fields WHERE id = 1)
          AND NOT EXISTS (
              SELECT 1
              FROM sensor_devices
              WHERE device_id = 'wokwi-demo-device'
          )
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DELETE FROM sensor_devices
        WHERE device_id = 'wokwi-demo-device'
          AND is_simulated = TRUE
        """
    )
