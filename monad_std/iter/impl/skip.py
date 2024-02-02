import typing as t
import collections.abc

from ..iter import IterMeta
from monad_std import Option

T = t.TypeVar('T')


class Skip(IterMeta[T], t.Generic[T]):
    __skipped: bool
    __skip_n: int
    __it: IterMeta[T]

    def __init__(self, it: IterMeta[T], n: int):
        self.__skipped = False
        self.__skip_n = n
        self.__it = it

    def next(self) -> Option[T]:
        if self.__skipped:
            return self.__it.next()
        else:
            for _ in range(self.__skip_n):
                if self.__it.next().is_none():
                    self.__skipped = True
                    return Option.none()
            self.__skipped = True
            return self.__it.next()
    