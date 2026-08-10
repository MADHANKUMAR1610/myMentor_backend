"""add social login columns

Revision ID: 413ba0002e54
Revises: c5fc2ce1353d
Create Date: 2026-08-08 00:12:58.986522

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.

revision: str = "413ba0002e54"

down_revision: Union[str, Sequence[str], None] = "c5fc2ce1353d"

branch_labels: Union[str, Sequence[str], None] = None

depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # ---------------------------------------------------------
    # 1. Add nullable columns first
    # ---------------------------------------------------------

    op.add_column(
        "users",
        sa.Column(
            "google_id",
            sa.String(length=255),
            nullable=True,
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "profile_image",
            sa.String(length=500),
            nullable=True,
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "login_provider",
            sa.String(length=20),
            nullable=True,
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "is_mobile_verified",
            sa.Boolean(),
            nullable=True,
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "is_email_verified",
            sa.Boolean(),
            nullable=True,
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=True,
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=True,
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=True,
        ),
    )

    # ---------------------------------------------------------
    # 2. Fill existing users
    # ---------------------------------------------------------

    op.execute(
        """
        UPDATE users
        SET
            login_provider = 'email',
            is_mobile_verified = FALSE,
            is_email_verified = TRUE,
            is_active = TRUE,
            created_at = NOW(),
            updated_at = NOW()
        WHERE login_provider IS NULL;
        """
    )

    # ---------------------------------------------------------
    # 3. Make required columns NOT NULL
    # ---------------------------------------------------------

    op.alter_column(
        "users",
        "login_provider",
        existing_type=sa.String(length=20),
        nullable=False,
    )

    op.alter_column(
        "users",
        "is_mobile_verified",
        existing_type=sa.Boolean(),
        nullable=False,
    )

    op.alter_column(
        "users",
        "is_email_verified",
        existing_type=sa.Boolean(),
        nullable=False,
    )

    op.alter_column(
        "users",
        "is_active",
        existing_type=sa.Boolean(),
        nullable=False,
    )

    op.alter_column(
        "users",
        "created_at",
        existing_type=sa.DateTime(),
        nullable=False,
    )

    op.alter_column(
        "users",
        "updated_at",
        existing_type=sa.DateTime(),
        nullable=False,
    )

    # ---------------------------------------------------------
    # 4. Add unique constraint for Google ID
    # ---------------------------------------------------------

    op.create_unique_constraint(
        "uq_users_google_id",
        "users",
        ["google_id"],
    )


def downgrade() -> None:
    """Downgrade schema."""

    # Remove unique constraint
    op.drop_constraint(
        "uq_users_google_id",
        "users",
        type_="unique",
    )

    # Remove columns
    op.drop_column(
        "users",
        "updated_at",
    )

    op.drop_column(
        "users",
        "created_at",
    )

    op.drop_column(
        "users",
        "is_active",
    )

    op.drop_column(
        "users",
        "is_email_verified",
    )

    op.drop_column(
        "users",
        "is_mobile_verified",
    )

    op.drop_column(
        "users",
        "login_provider",
    )

    op.drop_column(
        "users",
        "profile_image",
    )

    op.drop_column(
        "users",
        "google_id",
    )