import typing as t

from ..iter import IterMeta
from monad_std import Option

T = t.TypeVar('T')


class Enumerate(IterMeta[t.Tuple[int, T]], t.Generic[T]):
    __it: IterMeta[T]
    __num: int

    def __init__(self, __it: IterMeta[T]):
        self.__it = __it
        self.__num = 0

    def __self_add(self):
        self.__num += 1

    def next(self) -> Option[t.Tuple[int, T]]:
        return self.__it.next().map(lambda x: (self.__num, x)).inspect(lambda _: self.__self_add())

