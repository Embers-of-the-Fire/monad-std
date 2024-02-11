import typing as t

from ..iter import IterMeta
from monad_std import Option

It1 = t.TypeVar("It1", bound=IterMeta)
It2 = t.TypeVar("It2", bound=IterMeta)
T = t.TypeVar('T')
U = t.TypeVar('U')
B = t.TypeVar('B')


class Chain(IterMeta[T], t.Generic[T, It1, It2]):
    __it1: Option[It1]
    __it2: Option[It2]

    def __init__(self, one: Option[It1], another: Option[It2]):
        self.__it1 = one
        self.__it2 = another

    def __clear_it2(self) -> Option[T]:
        self.__it2 = Option.none()
        return Option.none()

    def __clear_it1(self) -> Option[T]:
        self.__it1 = Option.none()
        return self.__it2.and_then(lambda x: x.next()).or_else(lambda: self.__clear_it2())

    def next(self) -> Option[T]:
        return self.__it1.and_then(lambda x: x.next()).or_else(lambda: self.__clear_it1())
