import typing as t

from ..iter import IterMeta
from monad_std import Option

T = t.TypeVar('T')


class Filter(IterMeta[T], t.Generic[T]):
    __it: IterMeta[T]
    __func: t.Callable[[T], bool]

    def __init__(self, __it: IterMeta[T], __func: t.Callable[[T], bool]):
        self.__it = __it
        self.__func = __func

    def next(self) -> Option[T]:
        while (x := self.__it.next()).is_some():
            if self.__func(x.unwrap()):
                return x
        else:
            return Option.none()
    