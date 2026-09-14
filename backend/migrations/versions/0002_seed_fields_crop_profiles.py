"""seed fields, crop_profiles, crop_requirements, field_context_snapshots

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-23
"""

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        "fields",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("region_code", sa.String(10), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "crop_profiles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("source", sa.String(200), nullable=True),
        sa.Column("source_url", sa.String(500), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "crop_requirements",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("crop_profile_id", sa.Integer(), nullable=False),
        sa.Column("factor", sa.String(50), nullable=False),
        sa.Column("min_value", sa.Float(), nullable=False),
        sa.Column("max_value", sa.Float(), nullable=False),
        sa.Column("unit", sa.String(20), nullable=False),
        sa.Column("criticality", sa.String(20), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["crop_profile_id"],
            ["crop_profiles.id"],
            ondelete="CASCADE",
        ),
    )
    op.create_index(
        "ix_crop_requirements_crop_profile_id",
        "crop_requirements",
        ["crop_profile_id"],
    )

    op.create_table(
        "field_context_snapshots",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("field_id", sa.Integer(), nullable=False),
        sa.Column("soil_moisture", sa.Float(), nullable=True),
        sa.Column("ph", sa.Float(), nullable=True),
        sa.Column("temperature", sa.Float(), nullable=True),
        sa.Column("humidity", sa.Float(), nullable=True),
        sa.Column("light", sa.Float(), nullable=True),
        sa.Column("rainfall", sa.Float(), nullable=True),
        sa.Column(
            "captured_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["field_id"],
            ["fields.id"],
            ondelete="CASCADE",
        ),
    )
    op.create_index(
        "ix_field_context_snapshots_field_id",
        "field_context_snapshots",
        ["field_id"],
    )

    op.execute(
        """
        INSERT INTO fields (name, latitude, longitude, region_code) VALUES
        ('Pyinmana Demo Plot', 19.75, 96.13, 'MMR015')
        """
    )

    op.execute(
        """
        INSERT INTO crop_profiles (name, description, source, source_url) VALUES
        (
            'Maize',
            'Maize (Zea mays) general agronomic requirements for tropical varieties.',
            'FAO Ecocrop / Myanmar Agriculture Department',
            'https://ecocrop.fao.org'
        )
        """
    )

    op.execute(
        """
        INSERT INTO crop_requirements
            (crop_profile_id, factor, min_value, max_value, unit, criticality)
        VALUES
        (1, 'temperature', 18, 35, '°C', 'critical'),
        (1, 'soil_moisture', 40, 80, '%', 'important'),
        (1, 'ph', 5.5, 7.5, 'pH', 'critical'),
        (1, 'light', 60, 100, '%', 'important'),
        (1, 'rainfall', 500, 1500, 'mm', 'advisory'),
        (1, 'humidity', 40, 85, '%', 'advisory')
        """
    )

    op.execute(
        """
        INSERT INTO field_context_snapshots
            (field_id, soil_moisture, ph, temperature, humidity, light, rainfall)
        VALUES
            (1, 55.0, 6.2, 28.5, 70.0, 85.0, 1100.0)
        """
    )


def downgrade() -> None:
    op.drop_table("field_context_snapshots")
    op.drop_table("crop_requirements")
    op.drop_table("crop_profiles")
    op.drop_table("fields")
