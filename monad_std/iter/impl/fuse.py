import typing as t
import collections.abc

from ..iter import IterMeta
from monad_std import Option

T = t.TypeVar('T')


class Fuse(IterMeta[T], t.Generic[T]):
    __it: Option[IterMeta[T]]

    def __init__(self, it: IterMeta[T]):
        self.__it = Option.some(it)

    def __finish(self) -> Option[T]:
        self.__it = Option.none()
        return Option.none()

    def next(self) -> Option[T]:
        return self.__it.and_then(lambda x: x.next()).or_else(lambda: self.__finish())
