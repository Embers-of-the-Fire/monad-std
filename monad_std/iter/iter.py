from typing import Iterator, TypeVar, Generic, List, Iterable, Callable, Union
import collections.abc
from abc import ABCMeta, abstractmethod

from monad_std.option import Option
from monad_std.result import Result
from monad_std.error import UnwrapException

T = TypeVar("T")
U = TypeVar("U")


class IterMeta(Generic[T], Iterable[T], metaclass=ABCMeta):
    @staticmethod
    def iter(v: Union[Iterable[T], Iterator[T]]) -> "IterMeta[T]":
        """Convert an iterator or iterable object into `IterMeta`.

        For implementations, see [`_IterIterable`][monad_std.iter.iter._IterIterable] and
        [`_IterIterator`][monad_std.iter.iter._IterIterator].
        """
        if isinstance(v, collections.abc.Iterable):
            return _IterIterable(v)
        elif isinstance(v, collections.abc.Iterator):
            return _IterIterator(v)
        else:
            raise TypeError("expect an iterator or iterable object")

    @staticmethod
    def once(v: T) -> "IterMeta[T]":
        """Convert a single element into `IterMeta`.

        This method actually constructs a list and turns it into a [`_IterIterable`][monad_std.iter.iter._IterIterable].

        Examples:
            ```python
            element = 1
            it = IterMeta.once(element)
            assert it.next() == Option.of_some(1)
            assert it.next() == Option.of_none()
            ```
        """
        return _IterIterable([v])

    @abstractmethod
    def next(self) -> Option[T]:
        """Return the next element."""
        ...

    def __iter__(self):
        return self.to_iter()

    def array_chunk(self, chunk_size: int = 2) -> "_IterArrayChunk":
        """Returns an iterator over `N` elements of the iterator at a time.

        The chunks do not overlap. If `N` does not divide the length of the iterator, then the last up to `N-1`
        elements will be omitted and can be retrieved from the `get_unused()` method of the sub-iterator-class.

        Args:
            chunk_size: The number of elements to yield at a time, default 2. **Must be greater than zero!**

        Returns:
            See [`_IterArrayChunk`][monad_std.iter.rust_like._IterArrayChunk].

        Examples:
            ```python
            a = IterMeta.iter("loerm").array_chunk(2)
            assert a.next() == Option.of_some(['l', 'o'])
            assert a.next() == Option.of_some(['e', 'r'])
            assert a.next() == Option.of_none()
            assert a.get_unused().unwrap() == ['m']
            ```
        """
        return _IterArrayChunk(self, chunk_size)

    def chain(self, other: "IterMeta[T]") -> "_IterChain[T]":
        """Takes two iterators and creates a new iterator over both in sequence.

        `chain()` will return a new iterator which will first iterate over values from the first iterator and then
        over values from the second iterator. In other words, it links two iterators together, in a chain.

        [`once()`][monad_std.iter.iter.IterMeta.once] is commonly used to adapt a single value into a chain of other
        kinds of iteration.

        Args:
            other: Another iterator to chain with.

        Returns:
            See [`_IterChain`][monad_std.iter.rust_like._IterChain].

        Examples:
            ```python
            a1 = [1, 3, 5]
            a2 = [2, 4, 6]
            it1 = IterMeta.iter(a1)
            it2 = IterMeta.iter(a2)
            assert it1.chain(it2).collect_list() == [1, 3, 5, 2, 4 , 6]
            ```
        """
        return _IterChain(Option.of_some(self), Option.of_some(other))

    def enumerate(self) -> "_IterEnumerate[T]":
        """Creates an iterator which gives the current iteration count as well as the next value.

        The iterator returned yields pairs `(i, val)`, where `i` is the current index of iteration and `val` is the
        value returned by the iterator.

        `enumerate()` keeps its count as an `int` begining with `0`. If you want to count by a different value,
        the [`zip`][monad_std.iter.iter.IterMeta.zip] function provides similar functionality.

        Returns:
            See [`_IterEnumerate`][monad_std.iter.builtin_like._IterEnumerate].

        Examples:
            ```python
            a = ['a', 'b', 'c']
            it = IterMeta.iter(a).enumerate()
            assert it.next() == Option.of_some((0, 'a'))
            assert it.next() == Option.of_some((1, 'b'))
            assert it.next() == Option.of_some((2, 'c'))
            assert it.next() == Option.of_none()
            ```
        """
        return _IterEnumerate(self)

    def filter(self, func: Callable[[T], bool] = lambda x: x) -> "_IterFilter[T]":
        """Creates an iterator which uses a closure to determine if an element should be yielded.

        Given an element the closure must return `True` or `False`.
        The returned iterator will yield only the elements for which the closure returns `True`.

        If the closure is not specified, the method will return those are `True`.

        Note that `iter.filter(f).next()` is equivalent to [`iter.find(f)`][monad_std.iter.iter.IterMeta.find].

        Args:
            func: The closure to be used to determine if an element should be yielded.

        Returns:
            See [`_IterFilter`][monad_std.iter.builtin_like._IterFilter].

        Examples:
            ```python
            a = [-1, 0, 1, 2]
            it = IterMeta.iter(a)
            assert it.filter(lambda x: x > 0).collect_list() == [1, 2]
            ```
        """
        return _IterFilter(self, func)

    def filter_map(self, func: Callable[[T], Option[U]] = lambda x: Option.of_some(x)) -> "_IterFilterMap[T, U]":
        """Creates an iterator that both [`filter`][monad_std.iter.iter.IterMeta.filter]s
        and [`map`][monad_std.iter.iter.IterMeta.map]s.

        The returned iterator yields only the values for which the supplied closure returns `Some(value)`.

        `filter_map` can be used to make chains of filter and map more concise.

        Args:
            func:

        Returns:
            See [`_IterFilterMap`][monad_std.iter.rust_like._IterFilterMap].

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
        return _IterFilterMap(self, func)

    def flat_map(self, func: Callable[[T], Union[U, "IterMeta[U]", Iterable[U], Iterator[U]]]) -> "_IterFlatMap":
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
            See [`_IterFlatMap`][monad_std.iter.rust_like._IterFlatMap].

        Examples:
            ```python
            words = ["alpha", "beta", "gamma"]
            merged = IterMeta.iter(words).flat_map(iter).collect_string()
            assert merged == 'alphabetagamma'
        """
        return _IterFlatMap(self, func)

    def flatten(self) -> "_IterFlatten[T]":
        """Creates an iterator that flattens nested structure.

        This is useful when you have an iterator of iterators or an iterator of things that can be turned into
        iterators and you want to remove one level of indirection.

        Flattening works on any `Iterable` or `Iterator` type, including `Option` and `Result`.

        `flatten()` does not perform a **deep** flatten. Instead, only one level of nesting is removed. That is,
        if you `flatten()` a three-dimensional array, the result will be two-dimensional and not one-dimensional. To
        get a one-dimensional structure, you have to `flatten()` again.

        Returns:
            See [`_IterFlatten`][monad_std.iter.rust_like._IterFlatten].

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
            a = [Option.of_some(123), Result.of_ok(321), Option.of_none(), Option.of_some(233), Result.of_err('err')]
            ftd = IterMeta.iter(a).flatten().collect_list()
            assert ftd == [123, 321, 233]
            ```
        """
        return _IterFlatten(self)

    def fuse(self) -> "_IterFuse":
        """Creates an iterator which ends after the first `None`.

        After an iterator returns `None`, future calls may or may not yield `Some(T)` again.
        `fuse()` adapts an iterator, ensuring that after a `None` is given, it will always return `None` forever.

        Returns:
            See [`_IterFuse`][monad_std.iter.rust_like._IterFuse].

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
                        return Option.of_some(val)
                    else:
                        return Option.of_none()


            # we can see our iterator going back and forth
            it1 = NullableIterator(0)
            assert it1.next() == Option.of_some(0)
            assert it1.next() == Option.of_none()
            assert it1.next() == Option.of_some(2)
            assert it1.next() == Option.of_none()

            # however, once we fuse it...
            it2 = it1.fuse()
            assert it2.next() == Option.of_some(4)
            assert it2.next() == Option.of_none()

            # it will always return `None` after the first time.
            assert it2.next() == Option.of_none()
            assert it2.next() == Option.of_none()
            ```
        """
        return _IterFuse(self)

    def inspect(self, func: Callable[[T], None]) -> "_IterInspect[T]":
        """Does something with each element of an iterator, passing the value on.

        When using iterators, you’ll often chain several of them together. While working on such code, you might want
        to check out what’s happening at various parts in the pipeline. To do that, insert a call to `inspect()`.

        It’s more common for `inspect()` to be used as a debugging tool than to exist in your final code,
        but applications may find it useful in certain situations when errors need to be logged before being discarded.

        Returns:
            See [`_IterInspect`][monad_std.iter.rust_like._IterInspect].

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
        return _IterInspect(self, func)

    def intersperse(self, sep: T) -> "_IterIntersperse[T]":
        """Creates a new iterator which places a copy of separator between adjacent items of the original iterator.

        In case separator does not deepclonable or needs to be computed every time,
        use [`intersperse_with`][monad_std.iter.iter.IterMeta.intersperse_with].

        Args:
            sep: The separator to insert between each element.

        Returns:
            See [`_IterIntersperse`][monad_std.iter.rust_like._IterIntersperse].

        Examples:
            ```python
            it = IterMeta.iter([0, 1, 2]).intersperse(100)
            assert it.next() == Option.of_some(0)       # The first element from `a`.
            assert it.next() == Option.of_some(100)     # The separator.
            assert it.next() == Option.of_some(1)       # The next element from `a`.
            assert it.next() == Option.of_some(100)     # The separator.
            assert it.next() == Option.of_some(2)       # The last element from `a`.
            assert it.next() == Option.of_none()        # The iterator is finished.
            ```
            `intersperse` can be very useful to join an iterator’s items using a common element:
            ```python
            hello = IterMeta.iter(["Hello", "World", "!"]).intersperse(' ').collect_string()
            assert hello == "Hello World !"
            ```
        """
        return _IterIntersperse(self, sep)

    def intersperse_with(self, sep: Callable[[], T]) -> "_IterIntersperseWith[T]":
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
            See [`_IterIntersperseWith`][monad_std.iter.rust_like._IterIntersperseWith].

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
        return _IterIntersperseWith(self, sep)

    def map(self, func: Callable[[T], U]) -> "_IterMap[T, U]":
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
            See [`_IterMap`][monad_std.iter.builtin_like._IterMap].

        Examples:
            ```python
            a = [1, 2, 3]
            it = IterMeta.iter(a).map(lambda x: x * 2)
            assert it.next() == Option.of_some(2)
            assert it.next() == Option.of_some(4)
            assert it.next() == Option.of_some(6)
            assert it.next() == Option.of_none()
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
        return _IterMap(self, func)

    def peekable(self) -> "_IterPeekable[T]":
        """Creates an iterator which can use the `peek` method to look at the next element of the iterator without
        consuming it.

        Note that the underlying iterator is **still advanced** when `peek` is called for the first time: In order to
        retrieve the next element, [`next`][monad_std.iter.iter.IterMeta.next] is called on the underlying iterator,
        hence any side effects (i.e. anything other than fetching the next value) of the `next` method will occur.

        Returns:
            See [`_IterPeekable`][monad_std.iter.rust_like._IterPeekable].

        Examples:
            ```python
            xs = [1, 2, 3]
            it = IterMeta.iter(xs).peekable()

            # `peek()` lets us see into the future
            assert it.peek() == Option.of_some(1)
            assert it.next() == Option.of_some(1)

            # we can `peek()` multiple times, the iterator won't advance
            assert it.peek() == Option.of_some(2)
            assert it.peek() == Option.of_some(2)
            assert it.next() == Option.of_some(2)

            assert it.next() == Option.of_some(3)

            # after the iterator is finished, so is `peek()`
            assert it.peek() == Option.of_none()
            assert it.next() == Option.of_none()
            ```
        """
        return _IterPeekable(self)

    def zip(self, other: "IterMeta[U]") -> "_IterZip[T, U]":
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
            See [`_IterZip`][monad_std.iter.rust_like._IterZip].

        Examples:
            ```python
            a1 = [1, 3, 5]
            a2 = [2, 4, 6]
            it = IterMeta.iter(a1).zip(IterMeta.iter(a2))
            assert it.next() == Option.of_some((1, 2))
            assert it.next() == Option.of_some((3, 4))
            assert it.next() == Option.of_some((5, 6))
            assert it.next() == Option.of_none()
            ```
        """
        return _IterZip(self, other)

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

    def exist(self, item: T) -> bool:
        """A shortcut method for finding if an element exists in the iterator.

        `exist()` will try to call `__eq__`(alias `==`) on each element, please make sure your element implements that.

        `exist()` is short-circuiting, just like [`find`][monad_std.iter.iter.IterMeta.find].

        Args:
            item: The element to find.
        """
        return self.find(lambda x: x == item).is_some()

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
            assert IterMeta.iter(a).find(lambda x: x == 2) == Option.of_some(2)
            assert IterMeta.iter(a).find(lambda x: x == 5) == Option.of_none()
            ```
        """
        while (x := self.next()).is_some():
            uwp = x.unwrap()
            if predicate(uwp):
                return Option.of_some(uwp)
        return Option.of_none()

    def find_map(self, func: Callable[[T], Option[U]]) -> Option[U]:
        """Applies function to the elements of iterator and returns the first non-none result.

        `iter.find_map(f)` is equivalent to `iter.filter_map(f).next()`.

        Examples:
            ```python
            a = ["lol", "wow", "2", "5"]
            res = IterMeta.iter(a).find_map(lambda x: Result.catch_from(int, x).ok())
            assert res == Option.of_some(2)
            ```
        """
        while (x := self.next()).is_some():
            v = func(x.unwrap())
            if v.is_some():
                return v
        return Option.of_none()

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
            assert IterMeta.iter(a).position(lambda x: x == 2) == Option.of_some(1)
            assert IterMeta.iter(a).position(lambda x: x == 5) == Option.of_none()
            ```
        """
        idx = 0
        while (x := self.next()).is_some():
            if func(x.unwrap()):
                return Option.of_some(idx)
            else:
                idx += 1
        return Option.of_none()

    def product(self) -> Option[T]:
        """Iterates over the entire iterator, multiplying all the elements

        An empty iterator returns `None`.

        `product()` can be used to multiply any type implementing `__mul__/*`, including [`Option`]
        [monad_std.option.Option] and [`Result`][monad_std.result.Result].

        Examples:
            ```python
            assert IterMeta.iter(range(1, 6)).product() == Option.of_some(120)
            assert IterMeta.iter(range(1, 1)).product() == Option.of_none()
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
            assert reduced == Option.of_some(45)
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
            assert IterMeta.iter(a).sum() == Option.of_some(6)
            ```
        """
        return self.reduce(lambda x, y: x + y)

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
    _IterZip,
    _IterChain,
    _IterArrayChunk,
    _IterFilterMap,
    _IterFlatten,
    _IterFlatMap,
    _IterFuse,
    _IterInspect,
    _IterPeekable,
    _IterIntersperse,
    _IterIntersperseWith,
)
from .builtin_like import _IterMap, _IterFilter, _IterEnumerate
