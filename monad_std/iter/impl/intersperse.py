import typing as t

from ..iter import IterMeta
from monad_std import Option

from .peekable import Peekable

It = t.TypeVar("It", covariant=True, bound=IterMeta)
T = t.TypeVar('T')


class Intersperse(IterMeta[T], t.Generic[T, It]):
    __it: Peekable[T, It]
    __sep: T
    __need_sep: bool

    def __init__(self, it: It, sep: T):
        self.__it = it.peekable()
        self.__sep = sep
        self.__need_sep = False

    def next(self) -> Option[T]:
        if self.__need_sep and self.__it.peek().is_some():
            self.__need_sep = False
            return Option.some(self.__sep)
        else:
            self.__need_sep = True
            return self.__it.next()


class IntersperseWith(IterMeta[T], t.Generic[T, It]):
    __it: Peekable[T, It]
    __sep: t.Callable[[], T]
    __need_sep: bool

    def __init__(self, it: It, sep: t.Callable[[], T]):
        self.__it = it.peekable()
        self.__sep = sep
        self.__need_sep = False

    def next(self) -> Option[T]:
        if self.__need_sep and self.__it.peek().is_some():
            self.__need_sep = False
            return Option.some(self.__sep())
        else:
            self.__need_sep = True
            return self.__it.next()
        