import typing as t

from ..iter import IterMeta
from monad_std import Option

T = t.TypeVar("T", covariant=True)
B = t.TypeVar("B")


class Batching(IterMeta[B], t.Generic[T, B]):
    __it: IterMeta[T]
    __func: t.Callable[[IterMeta[T]], Option[B]]

    def __init__(self, __it: IterMeta[T], __func: t.Callable[[IterMeta[T]], Option[B]]):
        self.__it = __it
        self.__func = __func

    def next(self) -> Option[B]:
        return self.__func(self.__it)
