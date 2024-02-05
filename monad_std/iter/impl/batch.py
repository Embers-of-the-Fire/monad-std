import typing as t

from ..iter import IterMeta
from monad_std import Option

It = t.TypeVar("It", covariant=True, bound=IterMeta)
B = t.TypeVar("B")


class Batching(IterMeta[B], t.Generic[It, B]):
    __it: It
    __func: t.Callable[[It], Option[B]]

    def __init__(self, __it: It, __func: t.Callable[[It], Option[B]]):
        self.__it = __it
        self.__func = __func

    def next(self) -> Option[B]:
        return self.__func(self.__it)
