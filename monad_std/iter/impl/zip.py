import typing as t
import collections.abc

from ..iter import IterMeta
from monad_std import Option

T = t.TypeVar('T')
U = t.TypeVar('U')


class Zip(IterMeta[t.Tuple[T, U]], t.Generic[T, U]):
    __it1: IterMeta[T]
    __it2: IterMeta[U]

    def __init__(self, iter1: IterMeta[T], iter2: IterMeta[U]):
        self.__it1 = iter1
        self.__it2 = iter2

    def next(self) -> Option[t.Tuple[T, U]]:
        return self.__it1.next().zip(self.__it2.next())
