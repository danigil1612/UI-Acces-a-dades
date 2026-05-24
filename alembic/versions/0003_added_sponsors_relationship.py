"""Added sponsors relationship

Revision ID: 0003_sponsors
Revises: 0002_last_update
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0003_sponsors"
down_revision: Union[str, Sequence[str], None] = "0002_last_update"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "patrocinador",
        sa.Column("id_sponsor", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nom", sa.String(length=100), nullable=False),
        sa.Column("sector", sa.String(length=80), nullable=False),
        sa.Column("pais", sa.String(length=80), nullable=False),
        sa.Column(
            "last_update",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id_sponsor"),
        sa.UniqueConstraint("nom"),
    )

    op.create_table(
        "conductor_patrocinador",
        sa.Column("id_driver", sa.Integer(), nullable=False),
        sa.Column("id_sponsor", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["id_driver"], ["conductor.id_driver"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["id_sponsor"], ["patrocinador.id_sponsor"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id_driver", "id_sponsor"),
    )


def downgrade() -> None:
    op.drop_table("conductor_patrocinador")
    op.drop_table("patrocinador")
