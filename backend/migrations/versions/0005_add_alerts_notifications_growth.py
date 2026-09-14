"""add alerts, notification_deliveries, growth_simulations tables + assessment columns

Revision ID: 0005
Revises: 0004
Create Date: 2026-07-23
"""

import sqlalchemy as sa
from alembic import op

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.add_column(
        "assessments",
        sa.Column(
            "confidence",
            sa.String(20),
            server_default="high",
            nullable=False,
        ),
    )
    op.add_column(
        "assessments",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("field_id", sa.Integer(), nullable=False),
        sa.Column("assessment_id", sa.Integer(), nullable=False),
        sa.Column("fingerprint", sa.String(200), nullable=False),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("risk_type", sa.String(100), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column(
            "opened_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("acknowledged_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["field_id"], ["fields.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["assessment_id"], ["assessments.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_alerts_field_id", "alerts", ["field_id"])
    op.create_index("ix_alerts_fingerprint", "alerts", ["fingerprint"])

    op.create_table(
        "notification_deliveries",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("alert_id", sa.Integer(), nullable=False),
        sa.Column("channel", sa.String(30), nullable=False),
        sa.Column("destination_ref", sa.String(120), nullable=False),
        sa.Column("delivery_key", sa.String(220), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("attempt_count", sa.Integer(), nullable=False),
        sa.Column("last_error_code", sa.String(80), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("delivery_key"),
        sa.ForeignKeyConstraint(["alert_id"], ["alerts.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_notification_deliveries_alert_id", "notification_deliveries", ["alert_id"])

    op.create_table(
        "growth_simulations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("field_id", sa.Integer(), nullable=False),
        sa.Column("crop_profile_id", sa.Integer(), nullable=False),
        sa.Column("scenario_type", sa.String(30), nullable=False),
        sa.Column("seed", sa.String(80), nullable=False),
        sa.Column("is_illustrative", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["field_id"], ["fields.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["crop_profile_id"], ["crop_profiles.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_growth_simulations_field_id", "growth_simulations", ["field_id"])

    op.create_table(
        "growth_simulation_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("simulation_id", sa.Integer(), nullable=False),
        sa.Column("event_date", sa.String(10), nullable=False),
        sa.Column("growth_stage", sa.String(40), nullable=False),
        sa.Column("health_index", sa.Integer(), nullable=False),
        sa.Column("intervention", sa.Text(), nullable=True),
        sa.Column("risk_marker", sa.String(100), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["simulation_id"], ["growth_simulations.id"], ondelete="CASCADE"),
    )
    op.create_index(
        "ix_growth_simulation_events_simulation_id",
        "growth_simulation_events",
        ["simulation_id"],
    )


def downgrade() -> None:
    op.drop_table("growth_simulation_events")
    op.drop_table("growth_simulations")
    op.drop_table("notification_deliveries")
    op.drop_table("alerts")
    op.drop_column("assessments", "updated_at")
    op.drop_column("assessments", "confidence")
