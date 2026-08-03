"""add challenge timestamps

Revision ID: 8c7ff2bfebef
Revises: 52139533380f
Create Date: 2026-08-02 01:06:59.792690

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "8c7ff2bfebef"
down_revision: Union[str, Sequence[str], None] = "52139533380f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "challenges",
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=True,
        ),
    )

    op.add_column(
        "challenges",
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column(
        "challenges",
        "updated_at",
    )

    op.drop_column(
        "challenges",
        "created_at",
    )