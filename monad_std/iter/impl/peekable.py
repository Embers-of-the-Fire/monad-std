import typing as t

from ..iter import IterMeta
from monad_std import Option

T = t.TypeVar('T')


class Peekable(IterMeta[T], t.Generic[T]):
    __it: IterMeta[T]
    __peek: Option[Option[T]]

    def __init__(self, it: IterMeta[T]):
        self.__it = it
        self.__peek = Option.none()

    def next(self) -> Option[T]:
        pk = self.__peek
        self.__peek = Option.none()
        return pk.unwrap_or_else(lambda: self.__it.next())

    def __peek_next(self) -> Option[T]:
        pk = self.__it.next()
        self.__peek = Option.some(pk)
        return pk

    def peek(self) -> Option[T]:
        """Peek the next element of the inner iterator.

        Note that the underlying iterator is still advanced when `peek` is called for the first time:
        In order to retrieve the next element, `next` is called on the underlying iterator,
        hence any side effects (i.e. anything other than fetching the next value) of the next method will occur.

        Examples:
            ```python
            it = siter([1, 2, 3]).peekable()
            assert it.peek() == Option.some(1)
            assert it.next() == Option.some(1)
            assert it.peek() == Option.some(2)
            assert it.peek() == Option.some(2)
            assert it.next() == Option.some(2)
            assert it.next() == Option.some(3)
            assert it.peek() == Option.none()
            assert it.next() == Option.none()
            ```
        """
        return self.__peek.unwrap_or_else(lambda: self.__peek_next())
    