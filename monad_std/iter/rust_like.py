import typing as t
import collections.abc

from .iter import IterMeta
from .. import Option

T = t.TypeVar('T')
U = t.TypeVar('U')
B = t.TypeVar('B')


class Zip(IterMeta[t.Tuple[T, U]], t.Generic[T, U]):
    __it1: IterMeta[T]
    __it2: IterMeta[U]

    def __init__(self, iter1: IterMeta[T], iter2: IterMeta[U]):
        self.__it1 = iter1
        self.__it2 = iter2

    def next(self) -> Option[t.Tuple[T, U]]:
        return self.__it1.next().zip(self.__it2.next())


class Chain(IterMeta[T], t.Generic[T]):
    __it1: Option[IterMeta[T]]
    __it2: Option[IterMeta[T]]

    def __init__(self, one: Option[IterMeta[T]], another: Option[IterMeta[T]]):
        self.__it1 = one
        self.__it2 = another

    def __clear_it2(self) -> Option[T]:
        self.__it2 = Option.none()
        return Option.none()

    def __clear_it1(self) -> Option[T]:
        self.__it1 = Option.none()
        return self.__it2.and_then(lambda x: x.next()).or_else(lambda: self.__clear_it2())

    def next(self) -> Option[T]:
        return self.__it1.and_then(lambda x: x.next()).or_else(lambda: self.__clear_it1())


class ArrayChunk(IterMeta[t.List[T]], t.Generic[T]):
    __it: IterMeta[T]
    __chunk_size: int
    __unused: Option[t.List[T]]

    def __init__(self, it: IterMeta[T], chunk_size: int):
        assert chunk_size > 0, "Chunk size must be greater than zero!"
        self.__it = it
        self.__chunk_size = chunk_size

    def next(self) -> Option[t.List[T]]:
        arr = []
        for _ in range(self.__chunk_size):
            if (x := self.__it.next()).is_some():
                arr.append(x.unwrap())
            else:
                break
        else:
            # short-circuit here if we don't meet any Option::None
            return Option.some(arr)
        self.__unused = Option.some(arr)
        return Option.none()

    def get_unused(self) -> Option[t.List[T]]:
        """Return the last/unused several elements.

        Examples:
            ```python
            it = IterMeta.iter([1, 2, 3, 4]).array_chunk(3)
            assert it.next() == Option.some([1, 2, 3])
            assert it.next() == Option.none()
            assert it.get_unused() == Option.some([4])
            ```
        """
        return self.__unused


class Chunk(IterMeta[t.List[T]], t.Generic[T]):
    __it: ArrayChunk[T]
    __finished: bool

    def __init__(self, it: IterMeta[T], chunk_size: int):
        assert chunk_size > 0, "Chunk size must be greater than zero!"
        self.__it = it.array_chunk(chunk_size)
        self.__finished = False

    def next(self) -> Option[t.List[T]]:
        if not self.__finished:
            nxt = self.__it.next()
            if nxt.is_none():
                unused = self.__it.get_unused()
                self.__finished = True
                return unused
            return nxt
        else:
            return Option.none()


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


class Flatten(IterMeta[T], t.Generic[T]):
    __it: IterMeta[t.Union[T, IterMeta[T], t.Iterable[T], t.Iterator[T]]]
    __current_it: Option[IterMeta[T]]

    def __init__(self, it: IterMeta[t.Union[T, IterMeta[T], t.Iterable[T], t.Iterator[T]]]):
        self.__it = it
        self.__current_it = Option.none()

    def __it_next(self) -> Option[T]:
        if (nxt := self.__it.next()).is_some():
            nxt = nxt.unwrap()
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


class Fuse(IterMeta[T], t.Generic[T]):
    __it: Option[IterMeta[T]]

    def __init__(self, it: IterMeta[T]):
        self.__it = Option.some(it)

    def __finish(self) -> Option[T]:
        self.__it = Option.none()
        return Option.none()

    def next(self) -> Option[T]:
        return self.__it.and_then(lambda x: x.next()).or_else(lambda: self.__finish())


class Inspect(IterMeta[T], t.Generic[T]):
    __it: IterMeta[T]
    __func: t.Callable[[T], None]

    def __init__(self, it: IterMeta[T], func: t.Callable[[T], None]):
        self.__it = it
        self.__func = func

    def next(self) -> Option[T]:
        return self.__it.next().inspect(self.__func)


class Peekable(IterMeta[T], t.Generic[T]):
    __it: IterMeta[T]
    __peek: Option[Option[T]]

    def __init__(self, it: IterMeta[T]):
        self.__it = it
        self.__peek = Option.none()

    def next(self) -> Option[T]:
        pk = self.__peek
        self.__peek = Option.none()
        return pk.or_else(lambda: self.__it.next())

    def __peek_next(self) -> Option[T]:
        pk = self.__it.next()
        self.__peek = pk
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
        return self.__peek.or_else(lambda: self.__peek_next())


class Intersperse(IterMeta[T], t.Generic[T]):
    __it: Peekable[T]
    __sep: T
    __need_sep: bool

    def __init__(self, it: IterMeta[T], sep: T):
        self.__it = Peekable(it)
        self.__sep = sep
        self.__need_sep = False

    def next(self) -> Option[T]:
        if self.__need_sep and self.__it.peek().is_some():
            self.__need_sep = False
            return Option.some(self.__sep)
        else:
            self.__need_sep = True
            return self.__it.next()


class IntersperseWith(IterMeta[T], t.Generic[T]):
    __it: Peekable[T]
    __sep: t.Callable[[], T]
    __need_sep: bool

    def __init__(self, it: IterMeta[T], sep: t.Callable[[], T]):
        self.__it = Peekable(it)
        self.__sep = sep
        self.__need_sep = False

    def next(self) -> Option[T]:
        if self.__need_sep and self.__it.peek().is_some():
            self.__need_sep = False
            return Option.some(self.__sep())
        else:
            self.__need_sep = True
            return self.__it.next()


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


class Skip(IterMeta[T], t.Generic[T]):
    __skipped: bool
    __skip_n: int
    __it: IterMeta[T]

    def __init__(self, it: IterMeta[T], n: int):
        self.__skipped = False
        self.__skip_n = n
        self.__it = it

    def next(self) -> Option[T]:
        if self.__skipped:
            return self.__it.next()
        else:
            for _ in range(self.__skip_n):
                if self.__it.next().is_none():
                    self.__skipped = True
                    return Option.none()
            self.__skipped = True
            return self.__it.next()


class Take(IterMeta[T], t.Generic[T]):
    __remain: int
    __it: IterMeta[T]

    def __init__(self, it: IterMeta[T], take: int):
        self.__remain = take
        self.__it = it

    def next(self) -> Option[T]:
        if self.__remain != 0:
            self.__remain -= 1
            return self.__it.next()
        else:
            return Option.none()


class TakeWhile(IterMeta[T], t.Generic[T]):
    __func: t.Callable[[T], bool]
    __flag: bool
    __it: IterMeta[T]

    def __init__(self, it: IterMeta[T], func: t.Callable[[T], bool]):
        self.__func = func
        self.__it = it
        self.__flag = False

    def __while_check(self, value: T) -> Option[T]:
        if self.__func(value):
            return Option.some(value)
        else:
            self.__flag = True
            return Option.none()

    def next(self) -> Option[T]:
        if self.__flag:
            return Option.none()
        else:
            return self.__it.next().and_then(lambda x: self.__while_check(x))
