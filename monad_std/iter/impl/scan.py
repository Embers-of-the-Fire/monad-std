import typing as t

from ..iter import IterMeta
from monad_std import Option

T = t.TypeVar('T')
U = t.TypeVar('U')
B = t.TypeVar('B')


class Scan(IterMeta[B], t.Generic[T, B, U]):
    __it: IterMeta[T]
    __func: t.Callable[[U, T], t.Tuple[U, Option[B]]]
    __state: U

    def __init__(self, it: IterMeta[T], init: U, func: t.Callable[[U, T], t.Tuple[U, Option[B]]]):
        self.__it = it
        self.__func = func
        self.__state = init

    def __update_state(self, x: T) -> Option[B]:
        st, opt = self.__func(self.__state, x)
        self.__state = st
        return opt

    def next(self) -> Option[B]:
        return self.__it.next().and_then(lambda x: self.__update_state(x))
