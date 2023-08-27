from typing import TypeVar, Generic, Set

from ..option import Option

K = TypeVar('K')


class MSet(Generic[K], Set[K]):
    def pop(self) -> Option[K]:
        try:
            return Option.of_some(super().pop())
        except KeyError:
            return Option.of_none()
