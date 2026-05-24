from __future__ import annotations

from typing import Generic, Optional, Sequence, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session as SessioSQLAlchemy

from .db import SessionLocal
from .models import (
    Conductor,
    Cotxe,
    Cursa,
    Pista,
    Patrocinador,
    Pneumatic,
    ResultatCursa,
    ResultatPneumatic,
)

T = TypeVar("T")


class RepositoriBase(Generic[T]):
    def __init__(self, sessio: SessioSQLAlchemy, model: type[T]) -> None:
        self.sessio = sessio
        self.model = model

    def add(self, entitat: T) -> T:
        self.sessio.add(entitat)
        self.sessio.flush()
        return entitat

    def update(self, entitat: T) -> T:
        entitat_actualitzada = self.sessio.merge(entitat)
        self.sessio.flush()
        return entitat_actualitzada

    def get(self, id_entitat) -> Optional[T]:
        return self.sessio.get(self.model, id_entitat)

    def get_all(self) -> Sequence[T]:
        return self.sessio.scalars(select(self.model)).all()

    def delete(self, entitat_o_id) -> None:
        entitat = entitat_o_id
        if not isinstance(entitat_o_id, self.model):
            entitat = self.get(entitat_o_id)

        if entitat is not None:
            self.sessio.delete(entitat)
            self.sessio.flush()


class RepositoriConductor(RepositoriBase[Conductor]):
    def __init__(self, sessio: SessioSQLAlchemy) -> None:
        super().__init__(sessio, Conductor)

    def afegir_patrocinador(self, id_driver: int, id_sponsor: int) -> Conductor:
        conductor = self.get(id_driver)
        if conductor is None:
            raise ValueError(f"No existeix cap conductor amb id_driver={id_driver}.")

        patrocinador = self.sessio.get(Patrocinador, id_sponsor)
        if patrocinador is None:
            raise ValueError(f"No existeix cap patrocinador amb id_sponsor={id_sponsor}.")

        if patrocinador not in conductor.patrocinadors:
            conductor.patrocinadors.append(patrocinador)
            self.sessio.flush()
        return conductor

    def treure_patrocinador(self, id_driver: int, id_sponsor: int) -> Conductor:
        conductor = self.get(id_driver)
        if conductor is None:
            raise ValueError(f"No existeix cap conductor amb id_driver={id_driver}.")

        patrocinador = self.sessio.get(Patrocinador, id_sponsor)
        if patrocinador is None:
            raise ValueError(f"No existeix cap patrocinador amb id_sponsor={id_sponsor}.")

        if patrocinador in conductor.patrocinadors:
            conductor.patrocinadors.remove(patrocinador)
            self.sessio.flush()
        return conductor

    def get_by_numero(self, numero: int) -> Optional[Conductor]:
        return self.sessio.scalar(select(Conductor).where(Conductor.numero == numero))

    def get_by_nom(self, text: str) -> Sequence[Conductor]:
        return self.sessio.scalars(
            select(Conductor).where(Conductor.nom.ilike(f"%{text}%"))
        ).all()

    def get_by_nacionalitat(self, nacionalitat: str) -> Sequence[Conductor]:
        return self.sessio.scalars(
            select(Conductor).where(Conductor.nacionalitat == nacionalitat)
        ).all()


class RepositoriCotxe(RepositoriBase[Cotxe]):
    def __init__(self, sessio: SessioSQLAlchemy) -> None:
        super().__init__(sessio, Cotxe)

    def get_by_codi_xassis(self, codi_xassis: str) -> Optional[Cotxe]:
        return self.sessio.scalar(select(Cotxe).where(Cotxe.codi_xassis == codi_xassis))

    def get_by_proveidor_de_motors(self, proveidor: str) -> Sequence[Cotxe]:
        return self.sessio.scalars(
            select(Cotxe).where(Cotxe.proveidor_de_motors == proveidor)
        ).all()


class RepositoriPatrocinador(RepositoriBase[Patrocinador]):
    def __init__(self, sessio: SessioSQLAlchemy) -> None:
        super().__init__(sessio, Patrocinador)

    def get_by_nom(self, text: str) -> Sequence[Patrocinador]:
        return self.sessio.scalars(
            select(Patrocinador).where(Patrocinador.nom.ilike(f"%{text}%"))
        ).all()

    def get_by_sector(self, sector: str) -> Sequence[Patrocinador]:
        return self.sessio.scalars(
            select(Patrocinador).where(Patrocinador.sector == sector)
        ).all()


class RepositoriPista(RepositoriBase[Pista]):
    def __init__(self, sessio: SessioSQLAlchemy) -> None:
        super().__init__(sessio, Pista)

    def get_by_pais(self, pais: str) -> Sequence[Pista]:
        return self.sessio.scalars(select(Pista).where(Pista.pais == pais)).all()

    def get_by_nom(self, text: str) -> Sequence[Pista]:
        return self.sessio.scalars(select(Pista).where(Pista.nom.ilike(f"%{text}%"))).all()


class RepositoriCursa(RepositoriBase[Cursa]):
    def __init__(self, sessio: SessioSQLAlchemy) -> None:
        super().__init__(sessio, Cursa)

    def get_by_temporada(self, temporada: int) -> Sequence[Cursa]:
        return self.sessio.scalars(select(Cursa).where(Cursa.temporada == temporada)).all()

    def get_by_gran_premi(self, text: str) -> Sequence[Cursa]:
        return self.sessio.scalars(
            select(Cursa).where(Cursa.nom_del_gran_premi.ilike(f"%{text}%"))
        ).all()


class RepositoriPneumatic(RepositoriBase[Pneumatic]):
    def __init__(self, sessio: SessioSQLAlchemy) -> None:
        super().__init__(sessio, Pneumatic)

    def get_by_nom_compost(self, nom_compost: str) -> Optional[Pneumatic]:
        return self.sessio.scalar(
            select(Pneumatic).where(Pneumatic.nom_compost == nom_compost)
        )


class RepositoriResultatCursa(RepositoriBase[ResultatCursa]):
    def __init__(self, sessio: SessioSQLAlchemy) -> None:
        super().__init__(sessio, ResultatCursa)

    def get_by_conductor(self, id_driver: int) -> Sequence[ResultatCursa]:
        return self.sessio.scalars(
            select(ResultatCursa).where(ResultatCursa.id_driver == id_driver)
        ).all()

    def get_by_cursa(self, id_race: int) -> Sequence[ResultatCursa]:
        return self.sessio.scalars(
            select(ResultatCursa)
            .where(ResultatCursa.id_race == id_race)
            .order_by(ResultatCursa.posicio_final)
        ).all()

    def get_podi(self, id_race: int) -> Sequence[ResultatCursa]:
        return self.sessio.scalars(
            select(ResultatCursa)
            .where(ResultatCursa.id_race == id_race)
            .order_by(ResultatCursa.posicio_final)
            .limit(3)
        ).all()

    def get_paginated(self, page: int, page_size: int) -> Sequence[ResultatCursa]:
        if page < 1:
            raise ValueError("La pàgina ha de ser com a mínim 1.")
        if page_size < 1:
            raise ValueError("La mida de pàgina ha de ser com a mínim 1.")

        offset = (page - 1) * page_size
        return self.sessio.scalars(
            select(ResultatCursa)
            .order_by(ResultatCursa.id_result)
            .offset(offset)
            .limit(page_size)
        ).all()

    def afegir_pneumatic_a_resultat(
        self,
        id_result: int,
        id_tyre: int,
        periode: int,
        nombre_de_voltes: int,
        numero_us: int,
    ) -> ResultatPneumatic:
        resultat = self.get(id_result)
        if resultat is None:
            raise ValueError(f"No existeix cap resultat amb id_result={id_result}.")

        pneumatic = self.sessio.get(Pneumatic, id_tyre)
        if pneumatic is None:
            raise ValueError(f"No existeix cap pneumàtic amb id_tyre={id_tyre}.")

        us_pneumatic = ResultatPneumatic(
            id_result=id_result,
            id_tyre=id_tyre,
            periode=periode,
            nombre_de_voltes=nombre_de_voltes,
            numero_us=numero_us,
        )
        resultat.usos_pneumatics.append(us_pneumatic)
        self.sessio.flush()
        return us_pneumatic


class UnitatDeTreball:
    def __init__(self, session_factory=SessionLocal) -> None:
        self.session_factory = session_factory
        self.session: Optional[SessioSQLAlchemy] = None
        self.conductors: RepositoriConductor
        self.cotxes: RepositoriCotxe
        self.patrocinadors: RepositoriPatrocinador
        self.pistes: RepositoriPista
        self.curses: RepositoriCursa
        self.pneumatics: RepositoriPneumatic
        self.resultats: RepositoriResultatCursa

    def __enter__(self) -> "UnitatDeTreball":
        self.session = self.session_factory()
        self.conductors = RepositoriConductor(self.session)
        self.cotxes = RepositoriCotxe(self.session)
        self.patrocinadors = RepositoriPatrocinador(self.session)
        self.pistes = RepositoriPista(self.session)
        self.curses = RepositoriCursa(self.session)
        self.pneumatics = RepositoriPneumatic(self.session)
        self.resultats = RepositoriResultatCursa(self.session)
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if exc_type is not None:
            self.rollback()
        self.close()

    def commit(self) -> None:
        if self.session is None:
            raise RuntimeError("No hi ha cap sessió activa.")
        self.session.commit()

    def rollback(self) -> None:
        if self.session is not None:
            self.session.rollback()

    def close(self) -> None:
        if self.session is not None:
            self.session.close()
            self.session = None


UnitOfWork = UnitatDeTreball

ConductorRepository = RepositoriConductor
CotxeRepository = RepositoriCotxe
PatrocinadorRepository = RepositoriPatrocinador
PistaRepository = RepositoriPista
CursaRepository = RepositoriCursa
PneumaticRepository = RepositoriPneumatic
ResultatCursaRepository = RepositoriResultatCursa
