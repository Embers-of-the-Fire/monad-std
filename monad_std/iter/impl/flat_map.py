import typing as t
import collections.abc

from ..iter import IterMeta
from monad_std import Option

T = t.TypeVar('T')
U = t.TypeVar('U')


class FlatMap(IterMeta[U], t.Generic[T, U]):
    __it: IterMeta[T]
    __current_it: Option[IterMeta[U]]
    __func: t.Callable[[T], t.Union[U, IterMeta[U], t.Iterable[U], t.Iterator[U]]]

    def __init__(self, __it: IterMeta[T], __func: t.Callable[[T], t.Union[U, IterMeta[U], t.Iterable[U], t.Iterator[U]]]):
        self.__it = __it
        self.__func = __func
        self.__current_it = Option.none()

    def __it_next(self) -> Option[T]:
        if (nxt := self.__it.next()).is_some():
            nxtw = self.__func(nxt.unwrap())
            # noinspection DuplicatedCode
            if isinstance(nxt, IterMeta):
                self.__current_it = Option.some(nxt)
                return self.next()
            elif isinstance(nxt, (collections.abc.Iterator, collections.abc.Iterable)):
                self.__current_it = Option.some(IterMeta.iter(nxtw))
                return self.next()
            else:
                self.__current_it = Option.none()
                return Option.some(nxt)
        else:
            return Option.none()

    def next(self) -> Option[T]:
        if self.__current_it.is_some():
            x = self.__current_it.and_then(lambda s: s.next())
            if x.is_some():
                return x
            else:
                self.__current_it = Option.none()
        return self.__it_next()
