import typing as t

from ..iter import IterMeta
from monad_std import Option

T = t.TypeVar('T')
U = t.TypeVar('U')


class FilterMap(IterMeta[U], t.Generic[T, U]):
    __it: IterMeta[T]
    __func: t.Callable[[T], Option[U]]

    def __init__(self, it: IterMeta[T], func: t.Callable[[T], Option[U]]):
        self.__it = it
        self.__func = func

    def next(self) -> Option[U]:
        while (x := self.__it.next()).is_some():
            if (z := self.__func(x.unwrap())).is_some():
                return z
        else:
            return Option.none()
        