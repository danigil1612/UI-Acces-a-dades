"""Initial schema creation

Revision ID: 0001_initial_f1
Revises:
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001_initial_f1"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "conductor",
        sa.Column("id_driver", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nom", sa.String(length=100), nullable=False),
        sa.Column("nacionalitat", sa.String(length=60), nullable=False),
        sa.Column("numero", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id_driver"),
        sa.UniqueConstraint("numero"),
    )

    op.create_table(
        "pista",
        sa.Column("id_track", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nom", sa.String(length=100), nullable=False),
        sa.Column("pais", sa.String(length=80), nullable=False),
        sa.Column("longitud_km", sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint("id_track"),
    )

    op.create_table(
        "pneumatic",
        sa.Column("id_tyre", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nom_compost", sa.String(length=50), nullable=False),
        sa.Column("descripcio", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id_tyre"),
        sa.UniqueConstraint("nom_compost"),
    )

    op.create_table(
        "cotxe",
        sa.Column("id_cotxe", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("codi_xassis", sa.String(length=50), nullable=False),
        sa.Column("proveidor_de_motors", sa.String(length=80), nullable=False),
        sa.Column("potencia_cv", sa.Integer(), nullable=False),
        sa.Column("pes_kg", sa.Float(), nullable=False),
        sa.Column("id_driver", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["id_driver"], ["conductor.id_driver"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id_cotxe"),
        sa.UniqueConstraint("codi_xassis"),
        sa.UniqueConstraint("id_driver"),
    )

    op.create_table(
        "cursa",
        sa.Column("id_race", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nom_del_gran_premi", sa.String(length=120), nullable=False),
        sa.Column("data", sa.Date(), nullable=False),
        sa.Column("temporada", sa.Integer(), nullable=False),
        sa.Column("id_track", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["id_track"], ["pista.id_track"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id_race"),
    )
    op.create_index("ix_cursa_temporada", "cursa", ["temporada"])

    op.create_table(
        "resultat_cursa",
        sa.Column("id_result", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("posicio_final", sa.Integer(), nullable=False),
        sa.Column("punts", sa.Float(), nullable=False),
        sa.Column("temps_total", sa.String(length=40), nullable=True),
        sa.Column("id_driver", sa.Integer(), nullable=False),
        sa.Column("id_race", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["id_driver"], ["conductor.id_driver"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["id_race"], ["cursa.id_race"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id_result"),
        sa.UniqueConstraint("id_driver", "id_race", name="uq_resultat_conductor_cursa"),
    )
    op.create_index("ix_resultat_cursa_id_race", "resultat_cursa", ["id_race"])
    op.create_index("ix_resultat_cursa_id_driver", "resultat_cursa", ["id_driver"])

    op.create_table(
        "resultat_pneumatic",
        sa.Column("id_result", sa.Integer(), nullable=False),
        sa.Column("periode", sa.Integer(), nullable=False),
        sa.Column("id_tyre", sa.Integer(), nullable=False),
        sa.Column("nombre_de_voltes", sa.Integer(), nullable=False),
        sa.Column("numero_us", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["id_result"], ["resultat_cursa.id_result"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["id_tyre"], ["pneumatic.id_tyre"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id_result", "periode"),
    )


def downgrade() -> None:
    op.drop_table("resultat_pneumatic")
    op.drop_index("ix_resultat_cursa_id_driver", table_name="resultat_cursa")
    op.drop_index("ix_resultat_cursa_id_race", table_name="resultat_cursa")
    op.drop_table("resultat_cursa")
    op.drop_index("ix_cursa_temporada", table_name="cursa")
    op.drop_table("cursa")
    op.drop_table("cotxe")
    op.drop_table("pneumatic")
    op.drop_table("pista")
    op.drop_table("conductor")
