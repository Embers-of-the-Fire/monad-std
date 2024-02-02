import typing as t
import collections.abc

from ..iter import IterMeta
from monad_std import Option

T = t.TypeVar('T')


class Take(IterMeta[T], t.Generic[T]):
    __remain: int
    __it: IterMeta[T]

    def __init__(self, it: IterMeta[T], take: int):
        self.__remain = take
        self.__it = it

    def next(self) -> Option[T]:
        if self.__remain != 0:
            self.__remain -= 1
            return self.__it.next()
        else:
            return Option.none()


class TakeWhile(IterMeta[T], t.Generic[T]):
    __func: t.Callable[[T], bool]
    __flag: bool
    __it: IterMeta[T]

    def __init__(self, it: IterMeta[T], func: t.Callable[[T], bool]):
        self.__func = func
        self.__it = it
        self.__flag = False

    def __while_check(self, value: T) -> Option[T]:
        if self.__func(value):
            return Option.some(value)
        else:
            self.__flag = True
            return Option.none()

    def next(self) -> Option[T]:
        if self.__flag:
            return Option.none()
        else:
            return self.__it.next().and_then(lambda x: self.__while_check(x))
