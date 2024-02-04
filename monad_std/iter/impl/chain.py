import typing as t

from ..iter import IterMeta
from monad_std import Option

T = t.TypeVar('T')
U = t.TypeVar('U')
B = t.TypeVar('B')


class Chain(IterMeta[T], t.Generic[T]):
    __it1: Option[IterMeta[T]]
    __it2: Option[IterMeta[T]]

    def __init__(self, one: Option[IterMeta[T]], another: Option[IterMeta[T]]):
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
