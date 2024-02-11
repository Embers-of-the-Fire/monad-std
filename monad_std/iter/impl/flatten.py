import typing as t
import collections.abc

from ..iter import IterMeta
from monad_std import Option

T = t.TypeVar('T')
U = t.TypeVar('U')


class Flatten(IterMeta[T], t.Generic[T]):
    __it: IterMeta[t.Union[T, IterMeta[T], t.Iterable[T], t.Iterator[T]]]
    __current_it: Option[IterMeta[T]]

    def __init__(self, it: IterMeta[t.Union[T, IterMeta[T], t.Iterable[T], t.Iterator[T]]]):
        self.__it = it
        self.__current_it = Option.none()

    def __it_next(self) -> Option[T]:
        if (_nxt := self.__it.next()).is_some():
            nxt = _nxt.unwrap_unchecked()
            if isinstance(nxt, IterMeta):
                self.__current_it = Option.some(nxt)
                return self.next()
            elif isinstance(nxt, (collections.abc.Iterator, collections.abc.Iterable)):
                self.__current_it = Option.some(IterMeta.iter(nxt))
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
