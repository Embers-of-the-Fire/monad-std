from typing import TypeVar, Generic, Dict

from .pytuple import MTuple
from ..option import Option

K = TypeVar('K')
V = TypeVar('V')


class MDict(Generic[K, V], Dict[K, V]):
    def get(self, key: K) -> Option[V]:
        try:
            return Option.of_some(super().__getitem__(key))
        except KeyError:
            return Option.of_none()

    def popitem(self) -> Option[MTuple]:
        try:
            return Option.of_some(MTuple(super().popitem()))
        except KeyError:
            return Option.of_none()

    def pop(self, key: K) -> Option[V]:
        try:
            return Option.of_some(super().pop(key))
        except KeyError:
            return Option.of_none()
