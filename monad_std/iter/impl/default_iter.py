import typing as t

from monad_std.option import Option
from monad_std.result import Result, UnwrapException
from ..iter import IterMeta

T = t.TypeVar("T")


class _IterIterable(IterMeta[T], t.Generic[T]):
    __iter: t.Iterator[T]

    def __init__(self, v: t.Iterable[T]):
        self.__iter = iter(v)

    def next(self) -> Option[T]:
        return Result.catch(self.__iter.__next__).ok()


class _IterIterator(IterMeta[T], t.Generic[T]):
    __iter: t.Iterator[T]

    def __init__(self, v: t.Iterator[T]):
        self.__iter = v

    def next(self) -> Option[T]:
        return Result.catch(self.__iter.__next__).ok()


class _Iter(t.Iterator[T], t.Generic[T]):
    __iter: IterMeta[T]

    def __init__(self, v: IterMeta[T]):
        self.__iter = v

    def __next__(self):
        n = self.__iter.next()
        try:
            return n.unwrap()
        except UnwrapException:
            raise StopIteration
