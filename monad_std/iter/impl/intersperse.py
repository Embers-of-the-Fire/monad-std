import typing as t

from ..iter import IterMeta
from monad_std import Option

from .peekable import Peekable

T = t.TypeVar('T')


class Intersperse(IterMeta[T], t.Generic[T]):
    __it: Peekable[T]
    __sep: T
    __need_sep: bool

    def __init__(self, it: IterMeta[T], sep: T):
        self.__it = Peekable(it)
        self.__sep = sep
        self.__need_sep = False

    def next(self) -> Option[T]:
        if self.__need_sep and self.__it.peek().is_some():
            self.__need_sep = False
            return Option.some(self.__sep)
        else:
            self.__need_sep = True
            return self.__it.next()


class IntersperseWith(IterMeta[T], t.Generic[T]):
    __it: Peekable[T]
    __sep: t.Callable[[], T]
    __need_sep: bool

    def __init__(self, it: IterMeta[T], sep: t.Callable[[], T]):
        self.__it = Peekable(it)
        self.__sep = sep
        self.__need_sep = False

    def next(self) -> Option[T]:
        if self.__need_sep and self.__it.peek().is_some():
            self.__need_sep = False
            return Option.some(self.__sep())
        else:
            self.__need_sep = True
            return self.__it.next()
        