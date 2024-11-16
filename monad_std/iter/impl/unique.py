import typing as t

from ..iter import IterMeta
from monad_std import Option
import monad_std.typedef as td

Eq_T = t.TypeVar('Eq_T', bound=td.cmp.SupportsDunderHash)


class Unique(IterMeta[Eq_T], t.Generic[Eq_T]):
    __it: IterMeta[Eq_T]
    __found: t.Set[Eq_T]

    def __init__(self, it: IterMeta[Eq_T]):
        self.__it = it
        self.__found = set()

    def next(self) -> Option[Eq_T]:
        while (rx := self.__it.next()).is_some():
            x = rx.unwrap_unchecked()
            if x not in self.__found:
                self.__found.add(x)
                return Option.some(x)

        return Option.none()

