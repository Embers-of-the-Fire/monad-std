from typing import Iterator, TypeVar, Generic, List, Iterable, Callable, Union
import collections.abc
from abc import ABCMeta, abstractmethod

from monad_std.option import Option
from monad_std.result import Result, Err, Ok
from monad_std.error import UnwrapException

T = TypeVar("T")
U = TypeVar("U")
B = TypeVar("B")


class IterMeta(Generic[T], Iterable[T], metaclass=ABCMeta):
    @staticmethod
    def iter(v: "Union[Iterable[T@IterMeta], Iterator[T@IterMeta]]") -> "IterMeta[T]":
        """Convert an iterator or iterable object into `IterMeta`.

        For implementations, see [`_IterIterable`][monad_std.iter.iter._IterIterable] and
        [`_IterIterator`][monad_std.iter.iter._IterIterator].
        """
        if isinstance(v, collections.abc.Iterator):
            return _IterIterator(v)
        elif isinstance(v, collections.abc.Iterable):
            return _IterIterable(v)
        else:
            raise TypeError("expect an iterator or iterable object")

    @staticmethod
    def once(v: "T@IterMeta") -> "IterMeta[T]":
        """Convert a single element into `IterMeta`.

        This method actually constructs a list and turns it into an
        [`_IterIterable`][monad_std.iter.iter._IterIterable].

        Examples:
            ```python
            element = 1
            it = IterMeta.once(element)
            assert it.next() == Option.some(1)
            assert it.next() == Option.none()
            ```
        """
        return _IterIterable([v])

    @abstractmethod
    def next(self) -> Option[T]:
        """Return the next element."""
        ...

    def advance_by(self, n: int = 0) -> Result[None, int]:
        """Advances the iterator by `n` elements.

        This method will eagerly skip n elements by calling next up to n times until None is encountered.

        `advance_by(n)` will return `Ok(None)` if the iterator successfully advances by n elements, or an
        `Err(none-zero-int)` with value `k` if `None` is encountered, where `k` is remaining number of steps that
        could not be advanced because the iterator ran out. If self is empty and `n` is non-zero,
        then this returns `Err(n)`. Otherwise, `k` is always less than `n`.

        Calling `advance_by(0)` can do meaningful work, for example [`flatten`][monad_std.iter.iter.IterMeta.flatten]
        can advance its outer iterator until it finds an inner iterator that is not empty.

        Args:
            n: the number of elements to advance. Must be positive or zero.

        Returns:
            The result int will be between `0`(not include) and `n`(only when iterator is empty).

        Examples:
            ```python
            a = [1, 2, 3, 4]
            it = IterMeta.iter(a)
            assert it.advance_by(2) == Result.of_ok(None)
            assert it.next() == Option.some(3)
            assert it.advance_by(0) == Result.of_ok(None)
            assert it.advance_by(100) == Result.of_err(99)
            ```
        """
        for i in range(n):
            if self.next().is_none():
                return Err(n - i)
        return Ok(None)

    def last(self) -> Option[T]:
        """Consumes the iterator, returning the last element.

        This method will evaluate the iterator until it returns `None`. While doing so, it keeps track of the current
        element. After `None` is returned, `last()` will then return the last element it saw.

        Returns:
            If the iterator is empty, returns `None`. Otherwise, returns the last element.

        Examples:
            ```python
            a = [1, 2, 3]
            assert IterMeta.iter(a).last() == Option.some(3)
            a = []
            assert IterMeta.iter(a).last() == Option.none()
            ```
        """
        lst: Option[T] = Option.none()
        while (x := self.next()).is_some():
            lst = x
        return lst

    def next_chunk(self, n: int = 2) -> Result[List[T], List[T]]:
        """Advances the iterator and returns an array containing the next `N` values.

        If there are not enough elements to fill the array then `Err` is returned containing a list of the remaining
        elements.

        Returns:
            Returns a list of `N` elements. If there aren't enough elements, returns `Err` with the remaining.

        Examples:
            ```python
            a = [1, 2, 3]
            it = IterMeta.iter(a)
            assert it.next_chunk(2) == Ok([1, 2])
            assert it.next_chunk(2) == Err([3])
            ```
            Split a string and get the first three items:
            ```python
            quote = "not all those who wander are lost"
            first, second, third = IterMeta.iter(quote.split(' ')).next_chunk(3).unwrap()
            assert first == 'not'
            assert second == 'all'
            assert third == 'those'
            ```
        """
        ckl = []
        for _ in range(n):
            if (x := self.next()).is_some():
                ckl.append(x.unwrap())
            else:
                return Err(ckl)
        return Ok(ckl)

    def nth(self, n: int = 1) -> Option[T]:
        """Returns the `n`th element of the iterator.

        Like most indexing operations, the count starts from zero, so `nth(0)` returns the first value, `nth(1)` the
        second, and so on.

        Note that all preceding elements, as well as the returned element, will be consumed from the iterator. That
        means that the preceding elements will be discarded, and also that calling `nth(0)` multiple times on the
        same iterator will return different elements.

        `nth()` will return `None` if n is greater than or equal to the length of the iterator.

        Args:
            n: The target index of the element.

        Examples:
            ```python
            a = [1, 2, 3]
            assert IterMeta.iter(a).nth(1) == Option.some(2)
            ```
            Calling `nth()` multiple times doesn’t rewind the iterator:
            ```python
            a = [1, 2, 3]
            it = IterMeta.iter(a)
            assert it.nth(1) == Option.some(2)
            assert it.nth(1) == Option.none()
            ```
            Returning `None` if there are less than `n + 1` elements:
            ```python
            a = [1, 2, 3]
            assert IterMeta.iter(a).nth(10) == Option.none()
            ```
        """
        for i in range(n):
            if self.next().is_none():
                return Option.none()
        return self.next()

    def __iter__(self):
        return self.to_iter()

    def array_chunk(self, chunk_size: int = 2) -> "ArrayChunk":
        """Returns an iterator over `N` elements of the iterator at a time.

        The chunks do not overlap. If `N` does not divide the length of the iterator, then the last up to `N-1`
        elements will be omitted and can be retrieved from the `get_unused()` method of the sub-iterator-class.

        **Note:**
        The `ArrayChunk` does not yield the last several elements, and you should call
        [`ArrayChunk.get_unused`][monad_std.iter.rust_like.ArrayChunk.get_unused]
        method to get the last one(s).

        Args:
            chunk_size: The number of elements to yield at a time, default 2. **Must be greater than zero!**

        Returns:
            See [`ArrayChunk`][monad_std.iter.rust_like.ArrayChunk].

        Examples:
            ```python
            a = IterMeta.iter("loerm").array_chunk(2)
            assert a.next() == Option.some(['l', 'o'])
            assert a.next() == Option.some(['e', 'r'])
            assert a.next() == Option.none()
            assert a.get_unused().unwrap() == ['m']
            ```
        """
        return ArrayChunk(self, chunk_size)

    def chunk(self, chunk_size: int = 2) -> "Chunk[T]":
        """Returns an iterator over `N` elements of the iterator at a time,
        and also returns its last several uniter-ed elements.

        This will return a list of `N` elements unless the iterator cannot provide enough elements to fulfill
        a list of such length. Then this will return its last unused elements.

        Calling this is equivalent to calling [`array_chunk`][monad_std.iter.iter.IterMeta.array_chunk] and chaining
        the last unused elements, through the `get_unused` method.

        Args:
            chunk_size: The number of elements to yield at a time, default 2. **Must be greater than zero!**

        Returns:
            See [`Chunk`][monad_std.iter.rust_like.Chunk].

        Examples:
            ```python
            a = IterMeta.iter("loerm").chunk(2)
            assert a.next() == Option.some(['l', 'o'])
            assert a.next() == Option.some(['e', 'r'])
            assert a.next() == Option.some(['m'])
            assert a.next() == Option.none()
            ```
        """
        return Chunk(self, chunk_size)

    def chain(self, other: "IterMeta[T]") -> "Chain[T]":
        """Takes two iterators and creates a new iterator over both in sequence.

        `chain()` will return a new iterator which will first iterate over values from the first iterator and then
        over values from the second iterator. In other words, it links two iterators together, in a chain.

        [`once()`][monad_std.iter.iter.IterMeta.once] is commonly used to adapt a single value into a chain of other
        kinds of iteration.

        Args:
            other: Another iterator to chain with.

        Returns:
            See [`Chain`][monad_std.iter.rust_like.Chain].

        Examples:
            ```python
            a1 = [1, 3, 5]
            a2 = [2, 4, 6]
            it1 = IterMeta.iter(a1)
            it2 = IterMeta.iter(a2)
            assert it1.chain(it2).collect_list() == [1, 3, 5, 2, 4 , 6]
            ```
        """
        return Chain(Option.some(self), Option.some(other))

    def enumerate(self) -> "Enumerate[T]":
        """Creates an iterator which gives the current iteration count as well as the next value.

        The iterator returned yields pairs `(i, val)`, where `i` is the current index of iteration and `val` is the
        value returned by the iterator.

        `enumerate()` keeps its count as an `int` begining with `0`. If you want to count by a different value,
        the [`zip`][monad_std.iter.iter.IterMeta.zip] function provides similar functionality.

        Returns:
            See [`Enumerate`][monad_std.iter.builtin_like.Enumerate].

        Examples:
            ```python
            a = ['a', 'b', 'c']
            it = IterMeta.iter(a).enumerate()
            assert it.next() == Option.some((0, 'a'))
            assert it.next() == Option.some((1, 'b'))
            assert it.next() == Option.some((2, 'c'))
            assert it.next() == Option.none()
            ```
        """
        return Enumerate(self)

    def filter(self, func: Callable[[T], bool] = lambda x: x) -> "Filter[T]":
        """Creates an iterator which uses a closure to determine if an element should be yielded.

        Given an element the closure must return `True` or `False`.
        The returned iterator will yield only the elements for which the closure returns `True`.

        If the closure is not specified, the method will return those are `True`.

        Note that `iter.filter(f).next()` is equivalent to [`iter.find(f)`][monad_std.iter.iter.IterMeta.find].

        Args:
            func: The closure to be used to determine if an element should be yielded.

        Returns:
            See [`Filter`][monad_std.iter.builtin_like.Filter].

        Examples:
            ```python
            a = [-1, 0, 1, 2]
            it = IterMeta.iter(a)
            assert it.filter(lambda x: x > 0).collect_list() == [1, 2]
            ```
        """
        return Filter(self, func)

    def filter_map(self, func: Callable[[T], Option[U]] = lambda x: Option.some(x)) -> "FilterMap[T, U]":
        """Creates an iterator that both [`filter`][monad_std.iter.iter.IterMeta.filter]s
        and [`map`][monad_std.iter.iter.IterMeta.map]s.

        The returned iterator yields only the values for which the supplied closure returns `Some(value)`.

        `filter_map` can be used to make chains of filter and map more concise.

        Args:
            func:

        Returns:
            See [`FilterMap`][monad_std.iter.rust_like.FilterMap].

        Examples:
            The example below shows how a `map().filter().map()` can be shortened to a single call to `filter_map`.
            ```python
            a = ["1", "two", "3.0", "four", "5"]
            it1 = IterMeta.iter(a).filter_map(lambda x: Result.catch_from(float, x).ok())
            it2 = (IterMeta.iter(a)
                   .map(lambda x: Result.catch_from(float, x))
                   .filter(lambda x: x.is_ok())
                   .map(lambda x: x.unwrap()))
            assert it1.collect_list() == it2.collect_list()
            ```
        """
        return FilterMap(self, func)

    def flat_map(self, func: Callable[[T], Union[U, "IterMeta[U]", Iterable[U], Iterator[U]]]) -> "FlatMap":
        """Creates an iterator that works like map, but [`flatten`][monad_std.iter.iter.IterMeta.flatten]s
        nested structure.

        The [`map`][monad_std.iter.iter.IterMeta.map] adapter is very useful, but only when the closure argument
        produces values. If it produces an iterator instead, there’s an extra layer of indirection. `flat_map()`
        will remove this extra layer on its own.

        You can think of `flat_map` as the semantic equivalent of mapping,and then flattening as in `map().flatten()`.

        Another way of thinking about `flat_map()`: `map`’s closure returns one item for each element,
        and `flat_map()`’s closure returns an iterator for each element.

        Args:
            func: The function to apply to each element which produces an item or an iterator.

        Returns:
            See [`FlatMap`][monad_std.iter.rust_like.FlatMap].

        Examples:
            ```python
            words = ["alpha", "beta", "gamma"]
            merged = IterMeta.iter(words).flat_map(iter).collect_string()
            assert merged == 'alphabetagamma'
        """
        return FlatMap(self, func)

    def flatten(self) -> "Flatten[T]":
        """Creates an iterator that flattens nested structure.

        This is useful when you have an iterator of iterators or an iterator of things that can be turned into
        iterators and you want to remove one level of indirection.

        Flattening works on any `Iterable` or `Iterator` type, including `Option` and `Result`.

        `flatten()` does not perform a **deep** flatten. Instead, only one level of nesting is removed. That is,
        if you `flatten()` a three-dimensional array, the result will be two-dimensional and not one-dimensional. To
        get a one-dimensional structure, you have to `flatten()` again.

        Returns:
            See [`Flatten`][monad_std.iter.rust_like.Flatten].

        Examples:
            Basic usage:
            ```python
            a = [[1, 2, 3, 4], [5, 6]]
            ftd = IterMeta.iter(a).flatten().collect_list()
            assert ftd == [1, 2, 3, 4, 5, 6]
            ```
            Mapping and then flattening:
            ```python
            words = ["alpha", "beta", "gamma"]
            ftd = IterMeta.iter(words).map(iter).flatten().collect_string()
            assert ftd == 'alphabetagamma'
            ```
            Flattening works on any `Iterable` or `Iterator` type, including `Option` and `Result`:
            ```python
            a = [Option.some(123), Result.of_ok(321), Option.none(), Option.some(233), Result.of_err('err')]
            ftd = IterMeta.iter(a).flatten().collect_list()
            assert ftd == [123, 321, 233]
            ```
        """
        return Flatten(self)

    def fuse(self) -> "Fuse":
        """Creates an iterator which ends after the first `None`.

        After an iterator returns `None`, future calls may or may not yield `Some(T)` again.
        `fuse()` adapts an iterator, ensuring that after a `None` is given, it will always return `None` forever.

        Returns:
            See [`Fuse`][monad_std.iter.rust_like.Fuse].

        Examples:
            ```python
            class NullableIterator(IterMeta[int]):
                __state: int
                def __init__(self, state: int):
                    self.__state = state

                def next(self):
                    val = self.__state
                    self.__state += 1
                    if val % 2 == 0:
                        return Option.some(val)
                    else:
                        return Option.none()


            # we can see our iterator going back and forth
            it1 = NullableIterator(0)
            assert it1.next() == Option.some(0)
            assert it1.next() == Option.none()
            assert it1.next() == Option.some(2)
            assert it1.next() == Option.none()

            # however, once we fuse it...
            it2 = it1.fuse()
            assert it2.next() == Option.some(4)
            assert it2.next() == Option.none()

            # it will always return `None` after the first time.
            assert it2.next() == Option.none()
            assert it2.next() == Option.none()
            ```
        """
        return Fuse(self)

    def inspect(self, func: Callable[[T], None]) -> "Inspect[T]":
        """Does something with each element of an iterator, passing the value on.

        When using iterators, you’ll often chain several of them together. While working on such code, you might want
        to check out what’s happening at various parts in the pipeline. To do that, insert a call to `inspect()`.

        It’s more common for `inspect()` to be used as a debugging tool than to exist in your final code,
        but applications may find it useful in certain situations when errors need to be logged before being discarded.

        Returns:
            See [`Inspect`][monad_std.iter.rust_like.Inspect].

        Examples:
            ```python
            a = [1, 4, 2, 3]

            # this iterator sequence is complex.
            sumed = IterMeta.iter(a).filter(lambda x: x % 2 == 0).fold(0, lambda acc, x: acc + x)
            assert sumed == 6

            # let's add some `inspect()` calls to investigate what's happening
            sumed = (IterMeta.iter(a)
                   .inspect(lambda x: print(f'about to filter: {x}'))
                   .filter(lambda x: x % 2 == 0)
                   .inspect(lambda x: print(f'made it through filter: {x}'))
                   .fold(0, lambda acc, x: acc + x))
            assert sumed == 6
            ```
            This will print:
            ```text
            about to filter: 1
            about to filter: 4
            made it through filter: 4
            about to filter: 2
            made it through filter: 2
            about to filter: 3
            ```
        """
        return Inspect(self, func)

    def intersperse(self, sep: T) -> "Intersperse[T]":
        """Creates a new iterator which places a copy of separator between adjacent items of the original iterator.

        In case separator does not deepclonable or needs to be computed every time,
        use [`intersperse_with`][monad_std.iter.iter.IterMeta.intersperse_with].

        Args:
            sep: The separator to insert between each element.

        Returns:
            See [`Intersperse`][monad_std.iter.rust_like.Intersperse].

        Examples:
            ```python
            it = IterMeta.iter([0, 1, 2]).intersperse(100)
            assert it.next() == Option.some(0)       # The first element from `a`.
            assert it.next() == Option.some(100)     # The separator.
            assert it.next() == Option.some(1)       # The next element from `a`.
            assert it.next() == Option.some(100)     # The separator.
            assert it.next() == Option.some(2)       # The last element from `a`.
            assert it.next() == Option.none()        # The iterator is finished.
            ```
            `intersperse` can be very useful to join an iterator’s items using a common element:
            ```python
            hello = IterMeta.iter(["Hello", "World", "!"]).intersperse(' ').collect_string()
            assert hello == "Hello World !"
            ```
        """
        return Intersperse(self, sep)

    def intersperse_with(self, sep: Callable[[], T]) -> "IntersperseWith[T]":
        """Creates a new iterator which places an item generated by separator between adjacent items of the original
        iterator.

        The closure will be called exactly once each time an item is placed between two adjacent items from the
        underlying iterator; specifically, the closure is not called if the underlying iterator yields less than two
        items and after the last item is yielded.

        If the iterator’s item is deepclonable, it may be easier to use
        [`intersperse`][monad_std.iter.iter.IterMeta.intersperse].

        Args:
            sep: The function to produce the separator.

        Returns:
            See [`IntersperseWith`][monad_std.iter.rust_like.IntersperseWith].

        Examples:
            For ordinary usage it's recommended to use [`intersperse`][monad_std.iter.iter.IterMeta.intersperse],
            and here we'll show how `intersperse_with` can be used in situations where the separator
            needs to be computed:
            ```python
            src = IterMeta.iter(["Hello", "to", "all", "people", "!!"])
            happy_emojis = IterMeta.iter([" ❤️ ", " 😀 "])
            separator = lambda: happy_emojis.next().unwrap_or(" 🦀 ")
            result = src.intersperse_with(separator).collect_string()
            assert result == "Hello ❤️ to 😀 all 🦀 people 🦀 !!"
            ```
        """
        return IntersperseWith(self, sep)

    def map(self, func: Callable[[T], U]) -> "Map[T, U]":
        """Takes a closure and creates an iterator which calls that closure on each element.

        `map` transforms one iterator into another, by means of its argument.
        It produces a new iterator which calls this closure on each element of the original iterator.

        If you are good at thinking in types, you can think of `map` like this: If you have an iterator that gives
        you elements of some type `A`, and you want an iterator of some other type `B`, you can use `map`,
        passing a closure that takes an `A` and returns a `B`.

        `map` is conceptually similar to a for loop. However, as it is lazy, it is best used when you’re already
        working with other iterators. If you’re doing some sort of looping for a side effect, it’s considered more
        idiomatic to use for than `map`.

        Args:
            func: A closure to be called on each element.

        Returns:
            See [`Map`][monad_std.iter.builtin_like.Map].

        Examples:
            ```python
            a = [1, 2, 3]
            it = IterMeta.iter(a).map(lambda x: x * 2)
            assert it.next() == Option.some(2)
            assert it.next() == Option.some(4)
            assert it.next() == Option.some(6)
            assert it.next() == Option.none()
            ```
            If you’re doing some sort of side effect, prefer for to `map()`:
            ```python
            # don't do this:
            IterMeta.iter(range(5)).map(lambda x: print(f'number: {x}'));

            # it won't even execute, as it is lazy.

            # Instead, use for:
            for x in range(5):
                print(f'number: {x}')
            ```
        """
        return Map(self, func)

    def peekable(self) -> "Peekable[T]":
        """Creates an iterator which can use the `peek` method to look at the next element of the iterator without
        consuming it.

        Note that the underlying iterator is **still advanced** when `peek` is called for the first time: In order to
        retrieve the next element, [`next`][monad_std.iter.iter.IterMeta.next] is called on the underlying iterator,
        hence any side effects (i.e. anything other than fetching the next value) of the `next` method will occur.

        Returns:
            See [`Peekable`][monad_std.iter.rust_like.Peekable].

        Examples:
            ```python
            xs = [1, 2, 3]
            it = IterMeta.iter(xs).peekable()

            # `peek()` lets us see into the future
            assert it.peek() == Option.some(1)
            assert it.next() == Option.some(1)

            # we can `peek()` multiple times, the iterator won't advance
            assert it.peek() == Option.some(2)
            assert it.peek() == Option.some(2)
            assert it.next() == Option.some(2)

            assert it.next() == Option.some(3)

            # after the iterator is finished, so is `peek()`
            assert it.peek() == Option.none()
            assert it.next() == Option.none()
            ```
        """
        return Peekable(self)

    def scan(self, init: U, func: Callable[[U, T], B]) -> "Scan[T, B, U]":
        """An iterator adapter which, like fold, holds internal state, but unlike fold, produces a new iterator.

        `scan()` takes two arguments: an initial value which seeds the internal state, and a closure with two
        arguments, the first being the internal state and the second an iterator element. The closure can assign to
        the internal state to share state between iterations.

        On iteration, the closure will be applied to each element of the iterator and the return value from the
        closure, an Option(`Option[B]`), is returned by the next method, while the other value(`U`) replace the
        current state. Thus, the closure can return `Some(value)` to yield value, or `None` to end the iteration.

        Args:
            init: The initial state.
            func: The function to scan the iterator.

        Returns:
            See [`Scan`][monad_std.iter.rust_like.Scan].

        Examples:
            ```python
            a = [1, 2, 3, 4]

            def scanner(state: int, x: int):
                st = state * x
                if st > 6:
                    res = Option.none()
                else:
                    res = Option.some(-st)
                return st, res

            it = IterMeta.iter(a).scan(1, scanner)

            assert it.next() == Option.some(-1)
            assert it.next() == Option.some(-2)
            assert it.next() == Option.some(-6)
            assert it.next() == Option.none()
            ```
        """
        return Scan(self, init, func)

    def skip(self, n: int) -> "Skip[T]":
        """Creates an iterator that skips the first `n` elements.

        `skip(n)` skips elements until n elements are skipped or the end of the iterator is reached (whichever
        happens first). After that, all the remaining elements are yielded. In particular, if the original iterator
        is too short, then the returned iterator is empty.

        Args:
            n: The number of elements to skip.

        Returns:
            See [`Skip`][monad_std.iter.rust_like.Skip].

        Examples:
            ```python
            a = [1, 2, 3]
            it = IterMeta.iter(a).skip(2)
            assert it.next() == Option.some(3)
            assert it.next() == Option.none()
            assert it.next() == Option.none()
            ```
        """
        return Skip(self, n)

    def take(self, n: int) -> "Take[T]":
        """Creates an iterator that yields the first `n` elements, or fewer if the underlying iterator ends sooner.

        `take(n)` yields elements until `n` elements are yielded or the end of the iterator is reached (whichever
        happens first). The returned iterator is a prefix of length `n` if the original iterator contains at least
        `n` elements, otherwise it contains all the (fewer than `n`) elements of the original iterator.

        Args:
            n: The number of elements to take.

        Returns:
            See [`Take`][monad_std.iter.rust_like.Take].

        Examples:
            Basic usage:
            ```python
            a = [1, 2, 3]
            it = IterMeta.iter(a).take(2)
            assert it.next() == Option.some(1)
            assert it.next() == Option.some(2)
            assert it.next() == Option.none()
            ```
            `take()` is often used with an infinite iterator, to make it finite:
            ```python
            def fib():
                _f1 = 1
                _f2 = 1
                yield _f1
                yield _f2
                while True:
                    _f3 = _f1 + _f2
                    yield _f3
                    _f1 = _f2
                    _f2 = _f3

            it = IterMeta.iter(fib()).take(4)
            assert it.collect_list() == [1, 1, 2, 3]
            it = IterMeta.iter(fib()).skip(5).take(5)
            assert it.collect_list() == [8, 13, 21, 34, 55]
            ```
        """
        return Take(self, n)

    def take_while(self, func: Callable[[T], bool]) -> "TakeWhile[T]":
        """Creates an iterator that yields elements based on a predicate.

        `take_while()` takes a closure as an argument. It will call this closure on each element of the iterator, and yield elements while it returns `True`.

        After `False` is returned, `take_while()`’s job is over, and the rest of the elements are ignored.

        Args:
            func: The predicate function.

        Returns:
            See [`TakeWhile`][monad_std.iter.rust_like.TakeWhile].

        Examples:
            Basic usage:
            ```python
            a = [-1, 0, 1]
            it = IterMeta.iter(a).take_while(lambda v: v < 0)
            assert it.next() == Option.some(-1)
            assert it.next() == Option.none()
            ```
            Stopping after an initial `False`:
            ```python
            a = [-1, 0, 1, -2]
            it = IterMeta.iter(a).take_while(lambda v: v < 0)
            assert it.next() == Option.some(-1)
            assert it.next() == Option.none()
            assert it.next() == Option.none()
            assert it.next() == Option.none()
            ```
            Because `take_while()` needs to look at the value in order to see if it should be included or not,
            consuming iterators will see that it is removed:
            ```python
            a = [1, 2, 3, 4]
            it = IterMeta.iter(a)
            result = it.take_while(lambda v: v != 3).collect_list()
            assert result == [1, 2]
            result = it.collect_list()
            assert result == [4]
            ```
            The `3` is no longer there, because it was consumed in order to see if the iteration should stop,
            but wasn’t placed back into the iterator.
        """
        return TakeWhile(self, func)

    def zip(self, other: "IterMeta[U]") -> "Zip[T, U]":
        """‘Zips up’ two iterators into a single iterator of pairs.

        `zip()` returns a new iterator that will iterate over two other iterators, returning a tuple where the first
        element comes from the first iterator, and the second element comes from the second iterator.

        In other words, it zips two iterators together, into a single one.

        If either iterator returns `None`, next from the zipped iterator will return `None`. If the zipped iterator
        has no more elements to return then each further attempt to advance it will first try to advance the first
        iterator at most one time and if it still yielded an item try to advance the second iterator at most one time.

        Args:
            other: Another iterator to zip with.

        Returns:
            See [`Zip`][monad_std.iter.rust_like.Zip].

        Examples:
            ```python
            a1 = [1, 3, 5]
            a2 = [2, 4, 6]
            it = IterMeta.iter(a1).zip(IterMeta.iter(a2))
            assert it.next() == Option.some((1, 2))
            assert it.next() == Option.some((3, 4))
            assert it.next() == Option.some((5, 6))
            assert it.next() == Option.none()
            ```
        """
        return Zip(self, other)

    def to_iter(self) -> Iterator[T]:
        return _Iter(self)

    def count(self) -> int:
        """Count the size of the iterator.

        If you call `count` on the iterator, the **complete** iterator is consumed.
        """
        cnt = 0
        while self.next().is_some():
            cnt += 1
        return cnt

    def find(self, predicate: Callable[[T], bool]) -> Option[T]:
        """Searches for an element of an iterator that satisfies a predicate.

        `find()` takes a closure that returns `True` or `False`. It applies this closure to each element of the iterator,
        and if any of them return `True`, then `find()` returns `Some(element)`. If they all return `False`,
        it returns `None`.

        `find()` is short-circuiting; in other words, it will stop processing as soon as the closure returns `True`.

        If you need the index of the element, see [`position()`][monad_std.iter.iter.IterMeta.position].

        Args:
            predicate: The predicate to search for the element.

        Examples:
            ```python
            a = [1, 2, 3]
            assert IterMeta.iter(a).find(lambda x: x == 2) == Option.some(2)
            assert IterMeta.iter(a).find(lambda x: x == 5) == Option.none()
            ```
        """
        while (x := self.next()).is_some():
            uwp = x.unwrap()
            if predicate(uwp):
                return Option.some(uwp)
        return Option.none()

    def find_map(self, func: Callable[[T], Option[U]]) -> Option[U]:
        """Applies function to the elements of iterator and returns the first non-none result.

        `iter.find_map(f)` is equivalent to `iter.filter_map(f).next()`.

        Examples:
            ```python
            a = ["lol", "wow", "2", "5"]
            res = IterMeta.iter(a).find_map(lambda x: Result.catch_from(int, x).ok())
            assert res == Option.some(2)
            ```
        """
        while (x := self.next()).is_some():
            v = func(x.unwrap())
            if v.is_some():
                return v
        return Option.none()

    def fold(self, init: U, func: Callable[[U, T], U]) -> U:
        """Folds every element into an accumulator by applying an operation, returning the final result.

        fold() takes two arguments: an initial value, and a closure with two arguments: an accumulator,
        and an element. The closure returns the value that the accumulator should have for the next iteration.

        The initial value is the value the accumulator will have on the first call.

        After applying this closure to every element of the iterator, `fold()` returns the accumulator.

        This operation is sometimes called `reduce` or `inject`.

        Folding is useful whenever you have a collection of something, and want to produce a single value from it.

        **Note**: `fold`, and similar methods that traverse the entire iterator, might not terminate for infinite
        iterators, even on traits for which a result is determinable in finite time.

        **Note**: [`reduce`][monad_std.iter.iter.IterMeta.reduce] can be used to use the first element as the initial value,
        if the accumulator type and item type is the same.

        **Note**: `fold` combines elements in a left-associative fashion. For associative operators like +, the order the
        elements are combined in is not important, but for non-associative operators like - the order will affect the
        final result.

        In particular, try to have this call `fold` on the internal parts from which this iterator is composed.

        Args:
            init: The initial value.
            func: The function to be called.

        Examples:
            ```python
            a = [1, 2, 3]
            it = IterMeta.iter(a)
            assert it.fold(0, lambda acc, x: acc + x) == 6
            ```
            Let’s walk through each step of the iteration here:

            | element | acc  | x    | result |
            | ------- | ---- | ---- | ----- |
            |         | 0    |      |      |
            | 1       | 0   | 1    | 1     |
            | 2       | 1   | 2    | 3     |
            | 3       | 3   | 3    | 6     |

            And so, our final result, `6`.

            This example demonstrates the left-associative nature of `fold`: it builds a string,
            starting with an initial value and continuing with each element from the front until the back:

            ```python
            numbers = [1, 2, 3, 4, 5]
            result = IterMeta.iter(numbers).fold('0', lambda acc, x: f'({acc} + {x})')
            assert result == '(((((0 + 1) + 2) + 3) + 4) + 5)'
            ```
        """
        acc = init
        for v in self.to_iter():
            acc = func(acc, v)
        return acc

    def for_each(self, func: Callable[[T], None]) -> None:
        """Calls a closure on each element of an iterator.

        This is equivalent to using a [`for`](https://docs.python.org/3/reference/compound_stmts.html#the-for
        -statement) loop on the iterator, although break and continue are not possible from a closure. It’s generally
        more idiomatic to use a `for` loop, but `for_each` may be more legible when processing items at the end of
        longer iterator chains.

        Args:
            func: The function to execute.

        Examples:
            For such a small example, a `for` loop may be cleaner, but `for_each` might be preferable to keep a
            functional style with longer iterators:
            ```python
            (IterMeta.iter(range(5)).flat_map(lambda x: range(x * 100, x * 110))
                .enumerate()
                .filter(lambda i, x: (i + x) % 3 == 0)
                .for_each(lambda i, x: print(f"{i}:{x}")))
            ```
        """
        for i in self.to_iter():
            func(i)

    def index(self, item: T) -> Option[int]:
        """A shortcut method for finding an element in the iterator.

        `index()` will try to call `__eq__`(alias `==`) on each element, please make sure your element implements that.

        `index()` is short-circuiting, just like [`position`][monad_std.iter.iter.IterMeta.position].

        Args:
            item: The element to find.
        """
        return self.position(lambda x: x == item)

    def position(self, func: Callable[[T], bool]) -> Option[int]:
        """Searches for an element in an iterator, returning its index.

        `position()` takes a closure that returns true or false. It applies this closure to each element of the
        iterator, and if one of them returns `True`, then `position()` returns `Some(index)`. If all of them return
        `False`, it returns `None`.

        `position()` is short-circuiting; in other words, it will stop processing as soon as it finds a `True`.

        Args:
            func: The function to find the element.

        Examples:
            ```python
            a = [1, 2, 3]
            assert IterMeta.iter(a).position(lambda x: x == 2) == Option.some(1)
            assert IterMeta.iter(a).position(lambda x: x == 5) == Option.none()
            ```
        """
        idx = 0
        while (x := self.next()).is_some():
            if func(x.unwrap()):
                return Option.some(idx)
            else:
                idx += 1
        return Option.none()

    def product(self) -> Option[T]:
        """Iterates over the entire iterator, multiplying all the elements

        An empty iterator returns `None`.

        `product()` can be used to multiply any type implementing `__mul__/*`, including [`Option`]
        [monad_std.option.Option] and [`Result`][monad_std.result.Result].

        Examples:
            ```python
            assert IterMeta.iter(range(1, 6)).product() == Option.some(120)
            assert IterMeta.iter(range(1, 1)).product() == Option.none()
            ```
        """
        return self.reduce(lambda x, y: x * y)

    def reduce(self, func: Callable[[T, T], T]) -> Option[T]:
        """Reduces the elements to a single one, by repeatedly applying a reducing operation.

        If the iterator is empty, returns `None`; otherwise, returns the result of the reduction.

        The reducing function is a closure with two arguments: an accumulator, and an element. For iterators with at
        least one element, this is the same as `fold` with the first element of the iterator as the initial
        accumulator value, folding every subsequent element into it.

        Args:
            func: The function to call with iterator items.

        Examples:
            ```python
            reduced = IterMeta.iter(range(10)).reduce(lambda acc, e: acc + e)
            assert reduced == Option.some(45)
            assert reduced.unwrap() == IterMeta.iter(range(10)).fold(0, lambda acc, e: acc + e)
            ```
        """
        return self.next().map(lambda first: self.fold(first, func))

    def sum(self) -> Option[T]:
        """Sums the elements of an iterator.

        Takes each element, adds them together, and returns the result. If there's no element in the iterator,
        returns `None`

        `sum()` can be used to sum any type implementing `__add__/+`, including [`Option`][monad_std.option.Option] and
        [`Result`][monad_std.result.Result].

        Examples:
            ```python
            a = [1, 2, 3]
            assert IterMeta.iter(a).sum() == Option.some(6)
            ```
        """
        return self.reduce(lambda x, y: x + y)

    def exist(self, item: T) -> bool:
        """A shortcut method for finding if an element exists in the iterator.

        `exist()` will try to call `__eq__`(alias `==`) on each element, please make sure your element implements that.

        `exist()` is short-circuiting, just like [`find`][monad_std.iter.iter.IterMeta.find].

        Args:
            item: The element to find.
        """
        return self.find(lambda x: x == item).is_some()

    def all(self, func: Callable[[T], bool] = lambda x: x) -> bool:
        """Tests if every element of the iterator matches a predicate.

        `all()` takes a closure that returns `True` or `False`. It applies this closure to each element of the
        iterator, and if they all return `True`, then so does `all()`. If any of them return `False`, it returns
        `False`.

        `all()` is short-circuiting; in other words, it will stop processing as soon as it finds a `False`,
        given that no matter what else happens, the result will also be `False`.

        An empty iterator returns `True`.

        Args:
            func: The predicate function.

        Examples:
            ```python
            a = [1, 2, 3]
            assert IterMeta.iter(a).all(lambda x: x > 0)
            assert not IterMeta.iter(a).all(lambda x: x > 2)
            ```
            Stopping at the first `False`:
            ```python
            a = [1, 2, 3]
            it = IterMeta.iter(a)
            assert not it.all(lambda x: x != 2)

            # we can still use the iterator, as there are more elements.
            assert it.next() == Option.some(3)
            ```
        """
        while (x := self.next()).is_some():
            if func(x.unwrap()) is False:
                return False
        return True

    def any(self, func: Callable[[T], bool] = lambda x: x) -> bool:
        """Tests if any element of the iterator matches a predicate.

        `any()` takes a closure that returns `True` or `False`. It applies this closure to each element of the
        iterator, and if any of them return `True`, then so does `any()`. If they all return `False`, it returns
        `False`.

        `any()` is short-circuiting; in other words, it will stop processing as soon as it finds a `True`, given that
        no matter what else happens, the result will also be `True`.

        An empty iterator returns `False`.

        Args:
            func: The predicate function.

        Examples:
            ```python
            a = [1, 2, 3]
            assert IterMeta.iter(a).any(lambda x: x > 2)
            assert not IterMeta.iter(a).any(lambda x: x > 5)
            ```
            Stopping at the first `True`:
            ```python
            a = [1, 2, 3]
            it = IterMeta.iter(a)
            assert it.any(lambda x: x != 2)

            # we can still use the iterator, as there are more elements.
            assert it.next() == Option.some(2)
            ```
        """
        while (x := self.next()).is_some():
            if func(x.unwrap()) is True:
                return True
        return False

    def collect_list(self) -> List[T]:
        """Collect the iterator into a list."""
        return list(self.to_iter())

    def collect_tuple(self) -> tuple:
        """Collect the iterator into a tuple."""
        return tuple(self.to_iter())

    def collect_string(self) -> str:
        """Collect the iterator into a string. Using `__str__` but not `__repr__` as default."""
        return "".join(map(str, self.to_iter()))

    def collect_array(self):
        """Collect the iterator into a `funct.Array`.

        External Python library [funct](https://github.com/lauriat/funct) must be installed before using this feature.
        """
        try:
            import funct

            return funct.Array(self.to_iter())
        except ImportError:
            raise ImportError("You must install `funct` package to use this feature")


class MIterable(IterMeta[T], Generic[T]):
    __iter: Iterator[T]

    def __init__(self, v: Iterable[T]):
        self.__iter = iter(v)

    def next(self) -> Option[T]:
        return Result.catch(self.__iter.__next__).ok()

class _IterIterable(IterMeta[T], Generic[T]):
    __iter: Iterator[T]

    def __init__(self, v: Iterable[T]):
        self.__iter = iter(v)

    def next(self) -> Option[T]:
        return Result.catch(self.__iter.__next__).ok()


class _IterIterator(IterMeta[T], Generic[T]):
    __iter: Iterator[T]

    def __init__(self, v: Iterator[T]):
        self.__iter = v

    def next(self) -> Option[T]:
        return Result.catch(self.__iter.__next__).ok()


class _Iter(Iterator[T], Generic[T]):
    __iter: IterMeta[T]

    def __init__(self, v: IterMeta[T]):
        self.__iter = v

    def __next__(self):
        n = self.__iter.next()
        try:
            return n.unwrap()
        except UnwrapException:
            raise StopIteration

# Import types at the bottom of the file to avoid circular imports.
from .rust_like import (
    Zip,
    Chain,
    ArrayChunk,
    FilterMap,
    Flatten,
    FlatMap,
    Fuse,
    Inspect,
    Peekable,
    Intersperse,
    IntersperseWith,
    Scan,
    Skip,
    Take,
    TakeWhile,
    Chunk
)
from .builtin_like import Map, Filter, Enumerate
