import typing as t

from ..option import Option

K = t.TypeVar('K')


class MSet(t.Generic[K], t.Set[K]):
    def pop(self) -> Option[K]:
        try:
            return Option.some(super().pop())
        except KeyError:
            return Option.none()
