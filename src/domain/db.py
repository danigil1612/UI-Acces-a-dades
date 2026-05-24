from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import DB_URL

connect_args = {"check_same_thread": False} if DB_URL.startswith("sqlite") else {}

engine = create_engine(DB_URL, echo=False, future=True, connect_args=connect_args)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    future=True,
)
Session = SessionLocal


class Base(DeclarativeBase):
    pass


def crear_totes_les_taules() -> None:
    Base.metadata.create_all(engine)


def eliminar_totes_les_taules() -> None:
    Base.metadata.drop_all(engine)
