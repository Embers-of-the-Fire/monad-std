import typing as t
import collections.abc

from ..iter import IterMeta
from monad_std import Option

T = t.TypeVar('T')


class Inspect(IterMeta[T], t.Generic[T]):
    __it: IterMeta[T]
    __func: t.Callable[[T], None]

    def __init__(self, it: IterMeta[T], func: t.Callable[[T], None]):
        self.__it = it
        self.__func = func

    def next(self) -> Option[T]:
        return self.__it.next().inspect(self.__func)
