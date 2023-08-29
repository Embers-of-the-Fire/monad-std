from typing import TypeVar, Generic, Callable, Tuple, List, Union, Iterable, Iterator
import collections.abc

from .iter import IterMeta
from .. import Option

T = TypeVar('T')
U = TypeVar('U')


class _IterZip(Generic[T, U], IterMeta[Tuple[T, U]]):
    __it1: IterMeta[T]
    __it2: IterMeta[U]

    def __init__(self, iter1: IterMeta[T], iter2: IterMeta[U]):
        self.__it1 = iter1
        self.__it2 = iter2

    def next(self) -> Option[Tuple[T, U]]:
        return self.__it1.next().zip(self.__it2.next())


class _IterChain(Generic[T], IterMeta[T]):
    __it1: Option[IterMeta[T]]
    __it2: Option[IterMeta[T]]

    def __init__(self, one: Option[IterMeta[T]], another: Option[IterMeta[T]]):
        self.__it1 = one
        self.__it2 = another

    def __clear_it2(self) -> Option[T]:
        self.__it2 = Option.of_none()
        return Option.of_none()

    def __clear_it1(self) -> Option[T]:
        self.__it1 = Option.of_none()
        return self.__it2.and_then(lambda x: x.next()).or_else(lambda: self.__clear_it2())

    def next(self) -> Option[T]:
        return self.__it1.and_then(lambda x: x.next()).or_else(lambda: self.__clear_it1())


class _IterArrayChunk(Generic[T], IterMeta[List[T]]):
    __it: IterMeta[T]
    __chunk_size: int
    __unused: Option[List[T]]

    def __init__(self, it: IterMeta[T], chunk_size: int):
        assert chunk_size > 0, "Chunk size must be greater than zero!"
        self.__it = it
        self.__chunk_size = chunk_size

    def next(self) -> Option[List[T]]:
        arr = []
        for _ in range(self.__chunk_size):
            if (x := self.__it.next()).is_some():
                arr.append(x.unwrap())
            else:
                break
        else:
            # short-circuit here if we don't meet any Option::None
            return Option.of_some(arr)
        self.__unused = Option.of_some(arr)
        return Option.of_none()

    def get_unused(self) -> Option[List[T]]:
        return self.__unused


class _IterFilterMap(Generic[T, U], IterMeta[U]):
    __it: IterMeta[T]
    __func: Callable[[T], Option[U]]

    def __init__(self, it: IterMeta[T], func: Callable[[T], Option[U]]):
        self.__it = it
        self.__func = func

    def next(self) -> Option[U]:
        while (x := self.__it.next()).is_some():
            if (z := self.__func(x.unwrap())).is_some():
                return z
        else:
            return Option.of_none()


class _IterFlatten(Generic[T], IterMeta[T]):
    __it: IterMeta[Union[T, IterMeta[T], Iterable[T], Iterator[T]]]
    __current_it: Option[IterMeta[T]]

    def __init__(self, it: IterMeta[Union[T, IterMeta[T], Iterable[T], Iterator[T]]]):
        self.__it = it
        self.__current_it = Option.of_none()

    def __it_next(self) -> Option[T]:
        if (nxt := self.__it.next()).is_some():
            nxt = nxt.unwrap()
            if isinstance(nxt, IterMeta):
                self.__current_it = Option.of_some(nxt)
                return self.next()
            elif isinstance(nxt, (collections.abc.Iterator, collections.abc.Iterable)):
                self.__current_it = Option.of_some(IterMeta.iter(nxt))
                return self.next()
            else:
                self.__current_it = Option.of_none()
                return Option.of_some(nxt)
        else:
            return Option.of_none()

    def next(self) -> Option[T]:
        if self.__current_it.is_some():
            x = self.__current_it.and_then(lambda s: s.next())
            if x.is_some():
                return x
            else:
                self.__current_it = Option.of_none()
        return self.__it_next()


class _IterFlatMap(Generic[T, U], IterMeta[U]):
    __it: IterMeta[T]
    __current_it: Option[IterMeta[U]]
    __func: Callable[[T], Union[U, IterMeta[U], Iterable[U], Iterator[U]]]

    def __init__(self, __it: IterMeta[T], __func: Callable[[T], Union[U, IterMeta[U], Iterable[U], Iterator[U]]]):
        self.__it = __it
        self.__func = __func
        self.__current_it = Option.of_none()

    def __it_next(self) -> Option[T]:
        if (nxt := self.__it.next()).is_some():
            nxtw = self.__func(nxt.unwrap())
            # noinspection DuplicatedCode
            if isinstance(nxt, IterMeta):
                self.__current_it = Option.of_some(nxt)
                return self.next()
            elif isinstance(nxt, (collections.abc.Iterator, collections.abc.Iterable)):
                self.__current_it = Option.of_some(IterMeta.iter(nxtw))
                return self.next()
            else:
                self.__current_it = Option.of_none()
                return Option.of_some(nxt)
        else:
            return Option.of_none()

    def next(self) -> Option[T]:
        if self.__current_it.is_some():
            x = self.__current_it.and_then(lambda s: s.next())
            if x.is_some():
                return x
            else:
                self.__current_it = Option.of_none()
        return self.__it_next()


class _IterFuse(Generic[T], IterMeta[T]):
    __it: Option[IterMeta[T]]

    def __init__(self, it: IterMeta[T]):
        self.__it = Option.of_some(it)

    def __finish(self) -> Option[T]:
        self.__it = Option.of_none()
        return Option.of_none()

    def next(self) -> Option[T]:
        return self.__it.and_then(lambda x: x.next()).or_else(lambda: self.__finish())


class _IterInspect(Generic[T], IterMeta[T]):
    __it: IterMeta[T]
    __func: Callable[[T], None]

    def __init__(self, it: IterMeta[T], func: Callable[[T], None]):
        self.__it = it
        self.__func = func

    def next(self) -> Option[T]:
        return self.__it.next().inspect(self.__func)


class _IterPeekable(Generic[T], IterMeta[T]):
    __it: IterMeta[T]
    __peek: Option[Option[T]]

    def __init__(self, it: IterMeta[T]):
        self.__it = it
        self.__peek = Option.of_none()

    def next(self) -> Option[T]:
        pk = self.__peek
        self.__peek = Option.of_none()
        return pk.or_else(lambda: self.__it.next())

    def __peek_next(self) -> Option[T]:
        pk = self.__it.next()
        self.__peek = pk
        return pk

    def peek(self) -> Option[T]:
        return self.__peek.or_else(lambda: self.__peek_next())


class _IterIntersperse(Generic[T], IterMeta[T]):
    __it: _IterPeekable[T]
    __sep: T
    __need_sep: bool

    def __init__(self, it: IterMeta[T], sep: T):
        self.__it = _IterPeekable(it)
        self.__sep = sep
        self.__need_sep = False

    def next(self) -> Option[T]:
        if self.__need_sep and self.__it.peek().is_some():
            self.__need_sep = False
            return Option.of_some(self.__sep)
        else:
            self.__need_sep = True
            return self.__it.next()


class _IterIntersperseWith(Generic[T], IterMeta[T]):
    __it: _IterPeekable[T]
    __sep: Callable[[], T]
    __need_sep: bool

    def __init__(self, it: IterMeta[T], sep: Callable[[], T]):
        self.__it = _IterPeekable(it)
        self.__sep = sep
        self.__need_sep = False

    def next(self) -> Option[T]:
        if self.__need_sep and self.__it.peek().is_some():
            self.__need_sep = False
            return Option.of_some(self.__sep())
        else:
            self.__need_sep = True
            return self.__it.next()
