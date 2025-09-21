"""Restructure app_users and vendors; add contacts & locations table.

Revision ID: bc5942d7ce0f
Revises: de2a9f3a0339
Create Date: 2025-09-21 19:01:08.449022

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bc5942d7ce0f'
down_revision: Union[str, Sequence[str], None] = 'de2a9f3a0339'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Extend app_users
    op.add_column("app_users", sa.Column("full_name", sa.String(150)))
    op.add_column("app_users", sa.Column("email", sa.String(255), unique=True))
    op.add_column("app_users", sa.Column("profile_pic", sa.String(255)))
    op.add_column("app_users", sa.Column("fcm_token", sa.String(255)))

    # Extend vendors
    op.add_column("vendors", sa.Column("gst_number", sa.String(50)))
    op.add_column("vendors", sa.Column("website", sa.String(255)))

    # New table: contact_details
    op.create_table(
        "contact_details",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("contact_type", sa.String(50), nullable=False),
        sa.Column("value", sa.String(255), nullable=False),
        sa.Column("is_primary", sa.Boolean, default=False),
        sa.Column("user_id", sa.String, sa.ForeignKey("app_users.id", ondelete="CASCADE")),
        sa.Column("vendor_id", sa.Integer, sa.ForeignKey("vendors.id", ondelete="CASCADE")),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # New table: location_details
    op.create_table(
        "location_details",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("label", sa.String(100)),
        sa.Column("address_line1", sa.String(255), nullable=False),
        sa.Column("address_line2", sa.String(255)),
        sa.Column("city", sa.String(100)),
        sa.Column("state", sa.String(100)),
        sa.Column("country", sa.String(100)),
        sa.Column("postal_code", sa.String(20)),
        sa.Column("latitude", sa.Float),
        sa.Column("longitude", sa.Float),
        sa.Column("user_id", sa.String, sa.ForeignKey("app_users.id", ondelete="CASCADE")),
        sa.Column("vendor_id", sa.Integer, sa.ForeignKey("vendors.id", ondelete="CASCADE")),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )


def downgrade():
    # Rollback steps
    op.drop_table("location_details")
    op.drop_table("contact_details")

    op.drop_column("vendors", "website")
    op.drop_column("vendors", "gst_number")
    op.drop_column("vendors", "description")
    op.drop_column("vendors", "logo")

    op.drop_column("app_users", "fcm_token")
    op.drop_column("app_users", "profile_pic")
    op.drop_column("app_users", "email")
    op.drop_column("app_users", "full_name")
