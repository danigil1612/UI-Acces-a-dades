from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, Optional, Sequence, TypeVar

T = TypeVar("T")
ID = TypeVar("ID")


class AbstractRepository(ABC, Generic[T, ID]):
    @abstractmethod
    def add(self, entitat: T) -> T:
        raise NotImplementedError

    @abstractmethod
    def update(self, entitat: T) -> T:
        raise NotImplementedError

    @abstractmethod
    def get(self, id_entitat: ID) -> Optional[T]:
        raise NotImplementedError

    @abstractmethod
    def get_all(self) -> Sequence[T]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, entitat_o_id) -> None:
        raise NotImplementedError
