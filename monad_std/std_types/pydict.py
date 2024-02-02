import typing as t

from .pytuple import MTuple
from ..option import Option

K = t.TypeVar('K')
V = t.TypeVar('V')


class MDict(t.Generic[K, V], t.Dict[K, V]):
    def get(self, key: K) -> Option[V]:
        try:
            return Option.some(super().__getitem__(key))
        except KeyError:
            return Option.none()

    def popitem(self) -> Option[MTuple]:
        try:
            return Option.some(MTuple(super().popitem()))
        except KeyError:
            return Option.none()

    def pop(self, key: K) -> Option[V]:
        try:
            return Option.some(super().pop(key))
        except KeyError:
            return Option.none()
