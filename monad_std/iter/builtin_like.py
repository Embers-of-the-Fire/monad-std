from typing import TypeVar, Generic, Callable, Tuple

from .iter import IterMeta
from .. import Option

T = TypeVar('T')
U = TypeVar('U')


class _IterMap(IterMeta[U], Generic[T, U]):
    __it: IterMeta[T]
    __func: Callable[[T], U]

    def __init__(self, __it: IterMeta[T], __func: Callable[[T], U]):
        self.__it = __it
        self.__func = __func

    def next(self) -> Option[U]:
        return self.__it.next().map(self.__func)


class _IterFilter(IterMeta[T], Generic[T]):
    __it: IterMeta[T]
    __func: Callable[[T], bool]

    def __init__(self, __it: IterMeta[T], __func: Callable[[T], bool]):
        self.__it = __it
        self.__func = __func

    def next(self) -> Option[T]:
        while (x := self.__it.next()).is_some():
            if self.__func(x.unwrap()):
                return x
        else:
            return Option.none()


class _IterEnumerate(IterMeta[Tuple[int, T]], Generic[T]):
    __it: IterMeta[T]
    __num: int

    def __init__(self, __it: IterMeta[T]):
        self.__it = __it
        self.__num = 0

    def __self_add(self):
        self.__num += 1

    def next(self) -> Option[T]:
        return self.__it.next().map(lambda x: (self.__num, x)).inspect(lambda _: self.__self_add())

