"""add assessments table

Revision ID: 0004
Revises: 0003
Create Date: 2026-07-23
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSON

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        "assessments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("field_id", sa.Integer(), nullable=False),
        sa.Column("observation_id", sa.Integer(), nullable=True),
        sa.Column("crop_profile_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("health_score", sa.Float(), nullable=False),
        sa.Column("primary_risk", sa.String(100), nullable=True),
        sa.Column("recommendation", sa.Text(), nullable=True),
        sa.Column("evidence", JSON(), nullable=True),
        sa.Column("decision_mode", sa.String(20), nullable=False),
        sa.Column(
            "created_at",
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
        sa.ForeignKeyConstraint(
            ["observation_id"],
            ["sensor_observations.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["crop_profile_id"],
            ["crop_profiles.id"],
            ondelete="SET NULL",
        ),
    )
    op.create_index(
        "ix_assessments_field_id",
        "assessments",
        ["field_id"],
    )


def downgrade() -> None:
    op.drop_table("assessments")
