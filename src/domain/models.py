from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base




conductor_patrocinador = Table(
    "conductor_patrocinador",
    Base.metadata,
    Column(
        "id_driver",
        ForeignKey("conductor.id_driver", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "id_sponsor",
        ForeignKey("patrocinador.id_sponsor", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class AmbUltimaActualitzacio:
    last_update: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class Conductor(AmbUltimaActualitzacio, Base):
    __tablename__ = "conductor"

    id_driver: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nom: Mapped[str] = mapped_column(String(100), nullable=False)
    nacionalitat: Mapped[str] = mapped_column(String(60), nullable=False)
    numero: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)

    cotxe: Mapped[Optional["Cotxe"]] = relationship(
        back_populates="conductor",
        uselist=False,
        cascade="all, delete-orphan",
    )
    resultats: Mapped[list["ResultatCursa"]] = relationship(
        back_populates="conductor",
        cascade="all, delete-orphan",
    )
    patrocinadors: Mapped[list["Patrocinador"]] = relationship(
        secondary=conductor_patrocinador,
        back_populates="conductors",
    )

    def __repr__(self) -> str:
        return f"Conductor(id_driver={self.id_driver!r}, nom={self.nom!r})"


class Cotxe(AmbUltimaActualitzacio, Base):
    __tablename__ = "cotxe"

    id_cotxe: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codi_xassis: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    proveidor_de_motors: Mapped[str] = mapped_column(String(80), nullable=False)
    potencia_cv: Mapped[int] = mapped_column(Integer, nullable=False)
    pes_kg: Mapped[float] = mapped_column(Float, nullable=False)
    id_driver: Mapped[int] = mapped_column(
        ForeignKey("conductor.id_driver", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    conductor: Mapped["Conductor"] = relationship(back_populates="cotxe")

    def __repr__(self) -> str:
        return f"Cotxe(id_cotxe={self.id_cotxe!r}, codi_xassis={self.codi_xassis!r})"


class Patrocinador(AmbUltimaActualitzacio, Base):
    __tablename__ = "patrocinador"

    id_sponsor: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nom: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    sector: Mapped[str] = mapped_column(String(80), nullable=False)
    pais: Mapped[str] = mapped_column(String(80), nullable=False)

    conductors: Mapped[list["Conductor"]] = relationship(
        secondary=conductor_patrocinador,
        back_populates="patrocinadors",
    )

    def __repr__(self) -> str:
        return f"Patrocinador(id_sponsor={self.id_sponsor!r}, nom={self.nom!r})"


class Pista(AmbUltimaActualitzacio, Base):
    __tablename__ = "pista"

    id_track: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nom: Mapped[str] = mapped_column(String(100), nullable=False)
    pais: Mapped[str] = mapped_column(String(80), nullable=False)
    longitud_km: Mapped[float] = mapped_column(Float, nullable=False)

    curses: Mapped[list["Cursa"]] = relationship(
        back_populates="pista",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"Pista(id_track={self.id_track!r}, nom={self.nom!r})"


class Cursa(AmbUltimaActualitzacio, Base):
    __tablename__ = "cursa"

    id_race: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nom_del_gran_premi: Mapped[str] = mapped_column(String(120), nullable=False)
    data: Mapped[date] = mapped_column(Date, nullable=False)
    temporada: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    id_track: Mapped[int] = mapped_column(
        ForeignKey("pista.id_track", ondelete="RESTRICT"),
        nullable=False,
    )

    pista: Mapped["Pista"] = relationship(back_populates="curses")
    resultats: Mapped[list["ResultatCursa"]] = relationship(
        back_populates="cursa",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"Cursa(id_race={self.id_race!r}, gran_premi={self.nom_del_gran_premi!r})"


class Pneumatic(AmbUltimaActualitzacio, Base):
    __tablename__ = "pneumatic"

    id_tyre: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nom_compost: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    descripcio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    usos_en_resultats: Mapped[list["ResultatPneumatic"]] = relationship(
        back_populates="pneumatic",
    )

    def __repr__(self) -> str:
        return f"Pneumatic(id_tyre={self.id_tyre!r}, nom_compost={self.nom_compost!r})"


class ResultatCursa(AmbUltimaActualitzacio, Base):
    __tablename__ = "resultat_cursa"
    __table_args__ = (
        UniqueConstraint("id_driver", "id_race", name="uq_resultat_conductor_cursa"),
    )

    id_result: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    posicio_final: Mapped[int] = mapped_column(Integer, nullable=False)
    punts: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    temps_total: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    id_driver: Mapped[int] = mapped_column(
        ForeignKey("conductor.id_driver", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    id_race: Mapped[int] = mapped_column(
        ForeignKey("cursa.id_race", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    conductor: Mapped["Conductor"] = relationship(back_populates="resultats")
    cursa: Mapped["Cursa"] = relationship(back_populates="resultats")
    usos_pneumatics: Mapped[list["ResultatPneumatic"]] = relationship(
        back_populates="resultat",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"ResultatCursa(id_result={self.id_result!r}, posicio={self.posicio_final!r})"


class ResultatPneumatic(AmbUltimaActualitzacio, Base):
    __tablename__ = "resultat_pneumatic"

    id_result: Mapped[int] = mapped_column(
        ForeignKey("resultat_cursa.id_result", ondelete="CASCADE"),
        primary_key=True,
    )
    periode: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_tyre: Mapped[int] = mapped_column(
        ForeignKey("pneumatic.id_tyre", ondelete="RESTRICT"),
        nullable=False,
    )
    nombre_de_voltes: Mapped[int] = mapped_column(Integer, nullable=False)
    numero_us: Mapped[int] = mapped_column(Integer, nullable=False)

    resultat: Mapped["ResultatCursa"] = relationship(back_populates="usos_pneumatics")
    pneumatic: Mapped["Pneumatic"] = relationship(back_populates="usos_en_resultats")

    def __repr__(self) -> str:
        return (
            "ResultatPneumatic("
            f"id_result={self.id_result!r}, periode={self.periode!r}, id_tyre={self.id_tyre!r})"
        )
