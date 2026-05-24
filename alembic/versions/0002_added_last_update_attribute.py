"""Added last_update attribute

Revision ID: 0002_last_update
Revises: 0001_initial_f1
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0002_last_update"
down_revision: Union[str, Sequence[str], None] = "0001_initial_f1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TAULES = (
    "conductor",
    "cotxe",
    "pista",
    "cursa",
    "pneumatic",
    "resultat_cursa",
    "resultat_pneumatic",
)


def upgrade() -> None:
    for taula in TAULES:
        op.add_column(
            taula,
            sa.Column(
                "last_update",
                sa.DateTime(timezone=True),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
        )


def downgrade() -> None:
    for taula in reversed(TAULES):
        op.drop_column(taula, "last_update")
