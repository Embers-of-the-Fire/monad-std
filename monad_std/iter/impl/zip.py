import typing as t

from ..iter import IterMeta
from monad_std import Option

It1 = t.TypeVar("It1", covariant=True, bound=IterMeta)
It2 = t.TypeVar("It2", covariant=True, bound=IterMeta)
T = t.TypeVar('T')
U = t.TypeVar('U')


class Zip(IterMeta[t.Tuple[T, U]], t.Generic[T, U, It1, It2]):
    __it1: It1
    __it2: It2

    def __init__(self, iter1: It1, iter2: It2):
        self.__it1 = iter1
        self.__it2 = iter2

    def next(self) -> Option[t.Tuple[T, U]]:
        return self.__it1.next().zip(self.__it2.next())
