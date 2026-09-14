"""add health_updates, regions, ndvi_measurements tables

Revision ID: 0001
Revises:
Create Date: 2026-07-22
"""


import geoalchemy2  # noqa: F401
import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        "health_updates",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("township", sa.String(100), nullable=False),
        sa.Column("crop_type", sa.String(100), nullable=False),
        sa.Column("health_status", sa.String(50), nullable=False),
        sa.Column("disease_details", sa.Text(), nullable=True),
        sa.Column("reported_by", sa.String(100), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column(
            "reported_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "regions",
        sa.Column("pcode", sa.String(10), nullable=False),
        sa.Column("name_en", sa.String(100), nullable=False),
        sa.Column("name_my", sa.String(100), nullable=False),
        sa.PrimaryKeyConstraint("pcode"),
    )

    op.create_table(
        "ndvi_measurements",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("region_pcode", sa.String(10), nullable=False),
        sa.Column("label", sa.String(20), nullable=False),
        sa.Column("vim", sa.Float(), nullable=False),
        sa.Column("viq", sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_ndvi_measurements_region_pcode",
        "ndvi_measurements",
        ["region_pcode"],
    )

    op.execute(
        """
        INSERT INTO regions (pcode, name_en, name_my) VALUES
        ('MMR001', 'Sagaing Region', 'စစ်ကိုင်းတိုင်းဒေသကြီး'),
        ('MMR002', 'Bago Region', 'ပဲခူးတိုင်းဒေသကြီး'),
        ('MMR003', 'Magway Region', 'မကွေးတိုင်းဒေသကြီး'),
        ('MMR004', 'Mandalay Region', 'မန္တလေးတိုင်းဒေသကြီး'),
        ('MMR005', 'Tanintharyi Region', 'တနင်္သာရီတိုင်းဒေသကြီး'),
        ('MMR006', 'Ayeyarwady Region', 'ဧရာဝတီတိုင်းဒေသကြီး'),
        ('MMR007', 'Kachin State', 'ကချင်ပြည်နယ်'),
        ('MMR008', 'Kayah State', 'ကယားပြည်နယ်'),
        ('MMR009', 'Kayin State', 'ကရင်ပြည်နယ်'),
        ('MMR010', 'Chin State', 'ချင်းပြည်နယ်'),
        ('MMR011', 'Mon State', 'မွန်ပြည်နယ်'),
        ('MMR012', 'Rakhine State', 'ရခိုင်ပြည်နယ်'),
        ('MMR013', 'Shan State (North)', 'ရှမ်းပြည်နယ် (မြောက်ပိုင်း)'),
        ('MMR014', 'Yangon Region', 'ရန်ကုန်တိုင်းဒေသကြီး'),
        ('MMR015', 'Nay Pyi Taw', 'နေပြည်တော်'),
        ('MMR016', 'Shan State (South)', 'ရှမ်းပြည်နယ် (တောင်ပိုင်း)'),
        ('MMR017', 'Shan State (East)', 'ရှမ်းပြည်နယ် (အရှေ့ပိုင်း)'),
        ('MMR018', 'Bago Region (East)', 'ပဲခူးတိုင်းဒေသကြီး (အရှေ့ပိုင်း)')
        """
    )

    op.execute(
        """
        INSERT INTO ndvi_measurements (region_pcode, label, vim, viq) VALUES
        ('MMR001', 'Jan', 0.42, 72),
        ('MMR001', 'Feb', 0.48, 75),
        ('MMR001', 'Mar', 0.55, 79),
        ('MMR001', 'Apr', 0.62, 83),
        ('MMR001', 'May', 0.68, 87),
        ('MMR001', 'Jun', 0.71, 90)
        """
    )


def downgrade() -> None:
    op.drop_table("ndvi_measurements")
    op.drop_table("regions")
    op.drop_table("health_updates")
