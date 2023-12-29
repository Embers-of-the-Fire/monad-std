from typing import Generic, TypeVar, Optional, Callable, List, Tuple, Any, Iterator
from abc import ABCMeta, abstractmethod

from .error import UnwrapException

KT = TypeVar('KT')
T = TypeVar('T')
U = TypeVar('U')
E = TypeVar('E')
R = TypeVar('R')


__all__ = [
    "Option",
    "OpSome",
    "OpNone"
]


class Option(Generic[KT], metaclass=ABCMeta):
    """`Option` monad for python."""

    @abstractmethod
    def __bool__(self):
        """Returns `False` only if contained value is `None`."""
        ...

    @abstractmethod
    def __str__(self):
        ...

    @abstractmethod
    def __repr__(self):
        ...

    @abstractmethod
    def __eq__(self, other):
        ...

    @abstractmethod
    def __hash__(self):
        """`hash(Option)` has the same result as its contained value."""
        ...

    def __add__(self, other: "Option[Any]") -> "Option[Any]":
        """Alias `self.__value.__add__`.

        Returns:
            If both value are `Some`, this will return `Some(self + other)`. Otherwise, return `None`.
        """
        if isinstance(other, Option):
            if self.is_some() and other.is_some():
                return Option.some(self.unwrap().__add__(other.unwrap()))
            else:
                return Option.none()
        else:
            raise TypeError("expect another Option")

    def __mul__(self, other: "Option[Any]") -> "Option[Any]":
        """Alias `self.__value.__mul__`.

        Returns:
            If both value are `Ok`, this will return `Ok(self * other)`. Otherwise, return the first `Err`.
        """
        if isinstance(other, Option):
            if self.is_some() and other.is_some():
                return Option.some(self.unwrap() * other.unwrap())
            else:
                return Option.none()
        else:
            raise TypeError("expect a Result type")

    def __iter__(self) -> Iterator[KT]:
        return iter(self.to_array())

    def to_iter(self) -> Iterator[KT]:
        """Alias `iter(self.to_array())`."""
        return iter(self.to_array())

    def __and__(self, other):
        """Alias [`bool_and`][monad_std.option.Option.bool_and]."""
        if isinstance(other, Option):
            return self.bool_and(other)
        else:
            raise TypeError("expect another Option")

    def __or__(self, other):
        """Alias [`bool_or`][monad_std.option.Option.bool_or]."""
        if isinstance(other, Option):
            return self.bool_or(other)
        else:
            raise TypeError("expect another Option")

    def __xor__(self, other):
        """Alias [`bool_xor`][monad_std.option.Option.bool_xor]."""
        if isinstance(other, Option):
            return self.bool_xor(other)
        else:
            raise TypeError("expect another Option")

    @staticmethod
    def from_nullable(value: Optional[KT]) -> "Option[KT]":
        """Construct an `Option` from a nullable value."""
        if value is None:
            return OpNone()
        else:
            return OpSome(value)

    @staticmethod
    def some(value: KT) -> "Option[KT]":
        """ Create a value of `Some(KT)`.

        Args:
            value: Some value of type `KT`.

        Returns:
            `Option::Some(KT)`
        """
        return OpSome(value)

    @staticmethod
    def none() -> "Option[KT]":
        """ Create a value of `None`.

        Returns:
            `Option::None`
        """
        return OpNone()

    @abstractmethod
    def is_some(self) -> bool:
        """Returns `True` if the option is a `Some` value.

        Returns:
            Whether the option is a `Some` value.

        Examples:
            ```python
            x: Option[int] = Option.some(2)
            assert x.is_some()
            x: Option[int] = Option.none()
            assert not x.is_some()
            ```
        """
        ...

    @abstractmethod
    def is_none(self) -> bool:
        """Returns `True` if the option is a `None` value.

        Returns:
            Whether the option is a `None` value.

        Examples:
            ```python
            x: Option[int] = Option.some(2)
            assert not x.is_none()
            x: Option[int] = Option.none()
            assert x.is_none()
            ```
        """
        ...

    @abstractmethod
    def is_some_and(self, func: Callable[[KT], bool]) -> bool:
        """Returns true if the option is a `Some` and the value inside it matches a predicate.

        Args:
            func: A callable object which accepts the *not-none* value of the option and returns a boolean.

        Returns:
            Whether the option is a `Some` and the value inside it matches a predicate.

        Examples:
            ```python
            x: Option[int] = Option.some(2)
            assert x.is_some_and(lambda v: v > 1)
            x: Option[int] = Option.some(0)
            assert not x.is_some_and(lambda v: v > 1)
            x: Option[int] = Option.none()
            assert not x.is_some_and(lambda v: v > 1)
            ```
        """
        ...

    @abstractmethod
    def expect(self, msg: str) -> KT:
        """Returns the contained `Some` value.

        Returns the contained `Some` value, and raise an exception if the value is a `None` with a custom panic
        message provided by msg.

        **Recommended Message Style**

        We recommend that `expect` messages are used to describe the reason you *expect* the `Option` should be `Some`.

        ```python
        item = slice.get(0).expect("slice should not be empty");
        ```

        **Hint**: If you’re having trouble remembering how to phrase expect error messages,
        remember to focus on the word “should” as in “env variable should be set by blah”
        or “the given binary should be available and executable by the current user”.

        Args:
            msg: The message to display if this option is none.

        Returns:
            The contained `Some` value.

        Raises:
            error.UnwrapException: Raise an exception if the value is a `None` with a custom message provided by msg.

        Examples:
            ```python
            x: Option[str] = Option.some('value')
            assert x.expect('hey, this is an `Option::None` object') == 'value'
            x: Option[str] = Option.none()
            try:
                x.expect('hey, this is an `Option::None` object')
            except UnwrapException as e:
                assert str(e) == 'hey, this is an `Option::None` object'
            ```
        """
        ...

    @abstractmethod
    def to_pattern(self) -> Optional[KT]:
        """Returns the contained value for pattern-matching.

        This is the same as [`Option.to_nullable()`][monad_std.option.Option.to_nullable]."""
        ...

    @abstractmethod
    def to_nullable(self) -> Optional[KT]:
        """Returns the contained value. If `self` is an `Option::None`, this will return Python's `None` directly.

        **Note**: If the wrapped object is `None` itself, this will also return `None` as it's wrapped by the `Some`.
        It's impossible to distinguish between `Option::Some(None)` and `Option::None` by using this method.

        Returns:
            The contained value.

        Examples:
            ```python
            x: Option[str] = Option.some("air")
            assert x.to_nullable() == "air"
            x: Option[str] = Option.none()
            assert x.to_nullable() is None
            x: Option[None] = Option.some(None)
            assert x.to_nullable() is None
            ```
        """
        ...

    @abstractmethod
    def unwrap_unchecked(self) -> Optional[KT]:
        """Returns the contained value. If `self` is an `Option::None`, this will return Python's `None` directly.

        This is the same as [`Option.to_nullable()`][monad_std.option.Option.to_nullable]."""
        ...

    @abstractmethod
    def unwrap(self) -> KT:
        """Returns the contained `Some` value.

        Returns:
            The wrapped `Some` value.

        Raises:
            error.UnwrapException: Raise an exception if the value is a `None`.

        Examples:
            ```python
            x: Option[str] = Option.some("air")
            assert x.unwrap() == "air"
            x: Option[str] = Option.none()
            try:
                x.unwrap()
            except UnwrapException as e:
                assert str(e) == 'OptionError: call `Option.unwrap` on an `Option::None` object'
            ```
        """
        ...

    @abstractmethod
    def unwrap_or(self, default: KT) -> KT:
        """Returns the contained `Some` value or a provided default.

        Arguments passed to `unwrap_or` are eagerly evaluated.<br />If you are passing the result of a function call,
        it is recommended to use [`unwrap_or_else`][monad_std.option.Option.unwrap_or_else],
        which is lazily evaluated.

        Args:
            default: The default value.

        Returns:
            The contained `Some` value or a provided default.

        Examples:
            ```python
            assert Option.some("car").unwrap_or("bike") == "car"
            assert Option.none().unwrap_or("bike") == "bike"
            ```
        """
        ...

    @abstractmethod
    def unwrap_or_else(self, func: Callable[[], KT]) -> KT:
        """Returns the contained `Some` value or computes it from a callable object.

        Args:
            func: A callable object to compute.

        Examples:
            ```python
            k = 10
            assert Option.some(4).unwrap_or_else(lambda: 2 * k) == 4
            assert Option.none().unwrap_or_else(lambda: 2 * k) == 20
            ```
        """
        ...

    @abstractmethod
    def inspect(self, func: Callable[[KT], None]) -> "Option[KT]":
        """Calls the provided closure with the contained value (if `Some`), and return the option itself.

        Args:
            func: A callable object which accepts the wrapped value and returns nothing.

        Examples:
            ```python
            x = []
            Option.some(2).inspect(lambda s: x.append(s))
            assert x == [2]
            Option.none().inspect(lambda s: x.append(s))
            assert x == [2]
            ```
        """
        ...

    @abstractmethod
    def map(self, func: Callable[[KT], U]) -> "Option[U]":
        """Maps an `Option<KT>` to `Option<U>` by applying a function
        to a contained value (if `Some`) or returns `None` (if `None`).

        Args:
            func: A callable object that accepts the wrapped value and returns the processed value.

        Returns:
            Returns `Option::Some(U)` if the option is `Some` and returns `None` otherwise.

        Examples:
            ```python
            maybe_some_string = Option.some("Hello, World!")
            # `Option::map` will create a new option object
            maybe_some_len = maybe_some_string.map(lambda s: len(s))
            assert maybe_some_len == Option.some(13)
            assert Option.none().map(lambda s: len(s)) == Option.none()
            ```
        """
        ...

    @abstractmethod
    def map_mut(self, func: Callable[[KT], None]) -> "Option[KT]":
        """Maps and `Option<KT>` by changing its wrapped value.

        This method require a function to return nothing, and passes a reference into it.
        Actually, python doesn't differentiate mutable / immutable value,
        and this method is just for explicit notification.

        Args:
            func: A callable object that accepts the wrapped value.

        Examples:
            ```python
            class Test:
                value: int
                def __init__(self, val: int):
                    self.value = val

                def change_value(self, new_value: int):
                    print('old:', self.value, 'new:', new_value)
                    self.value = new_value

            maybe_something = Option.some(Test(1))
            assert maybe_something.unwrap().value == 1
            maybe_something.map_mut(lambda x: x.change_value(5))
            assert maybe_something.unwrap().value == 5
            ```
        """
        ...

    @abstractmethod
    def map_or(self, default: U, func: Callable[[KT], U]) -> U:
        """Returns the provided default result (if none), or applies a function to the contained value (if any).

        Arguments passed to map_or are eagerly evaluated.<br />If you are passing the result of a function call,
        it is recommended to use [`map_or_else`][monad_std.option.Option.map_or_else], which is lazily evaluated.

        Args:
            default: The default value if the option is `None`.
            func: The function to apply to the contained value.

        Examples:
            ```python
            assert Option.some('foo').map_or(42, lambda s: len(s)) == 3
            assert Option.none().map_or(42, lambda s: len(s)) == 42
            ```
        """
        ...

    @abstractmethod
    def map_or_else(self, default: Callable[[], U], func: Callable[[KT], U]) -> U:
        """Computes a default function result (if none),
        or applies a different function to the contained value (if any).

        Args:
            default: The function to produce a default value.
            func: The function to apply to the contained value.

        Examples:
            ```python
            k = 21
            assert Option.some('bar').map_or_else(lambda: 2 * k, lambda s: len(s)) == 3
            assert Option.none().map_or_else(lambda: 2 * k, lambda s: len(s)) == 42
            ```
        """
        ...

    @abstractmethod
    def ok_or(self, err: E) -> "Result[KT, E]":
        """Transforms the `Option<KT>` into a `Result<KT, E>`, mapping `Some(v)` to `Ok(v)` and `None` to `Err(err)`.

        Arguments passed to ok_or are eagerly evaluated.<br />
        If you are passing the result of a function call,
        it is recommended to use [`ok_or_else`][monad_std.option.Option.ok_or_else], which is lazily evaluated.

        Args:
            err: A value representing an error

        Examples:
            ```python
            assert Option.some('foo').ok_or(0) == Result.of_ok('foo')
            assert Option.none().ok_or(0) == Result.of_err(0)
            ```
        """
        ...

    @abstractmethod
    def ok_or_else(self, err: Callable[[], E]) -> "Result[KT, E]":
        """Transforms the `Option<KT>` into a `Result<KT, E>`, mapping `Some(v)` to `Ok(v)` and `None` to `Err(err())`.

        Args:
            err: A callable object that returns an error value.

        Examples:
            ```python
            k = 21
            assert Option.some('foo').ok_or_else(lambda: k * 2) == Result.of_ok('foo')
            assert Option.none().ok_or_else(lambda: k * 2) == Result.of_err(42)
            ```
        """
        ...

    @abstractmethod
    def to_array(self) -> List[KT]:
        """Returns an array of the possible contained value.

        Examples:
            ```python
            assert Option.some(1).to_array() == [1]
            assert Option.none().to_array() == []
            ```
        """
        ...

    @abstractmethod
    def bool_and(self, optb: "Option[U]") -> "Option[U]":
        """Returns None if the option is `None`, otherwise returns `optb`. Alias `&(__and__)`.

        `and` is a keyword in Python, so here we use `bool_and` instead.

        Arguments passed to and are eagerly evaluated.<br />
        If you are passing the result of a function call,
        it is recommended to use [`and_then`][monad_std.option.Option.and_then], which is lazily evaluated.

        Args:
            optb: Another option object to do the bool evaluation.

        Examples:
            ```python
            assert Option.some(2).bool_and(Option.none()) == Option.none()
            assert Option.none().bool_and(Option.some('foo')) == Option.none()
            assert Option.some(2).bool_and(Option.some('bar')) == Option.some('bar')
            assert Option.none().bool_and(Option.none()) == Option.none()
            ```
        """
        ...

    @abstractmethod
    def and_then(self, func: Callable[[KT], "Option[U]"]) -> "Option[U]":
        """Returns `None` if the option is `None`,
        otherwise calls `func` with the wrapped value and returns the result. Alias `flatmap`.

        Args:
            func: A callable object to produce the next value.

        Examples:
            ```python
            assert Option.some(2).and_then(lambda x: Option.some(str(x))) == Option.some('2')
            assert Option.some(10).and_then(lambda _: Option.none()) == Option.none()
            assert Option.none().and_then(lambda x: Option.some(str(x))) == Option.none()
            ```
            Often used to chain fallible operations that may return `None`.
            ```python
            def get_from(l, i):
                try:
                    return Option.some(l[i])
                except IndexError:
                    return Option.none()

            arr_2d = [["A0", "A1"], ["B0", "B1"]]
            assert get_from(arr_2d, 0).and_then(lambda row: get_from(row, 1)) == Option.some('A1')
            assert get_from(arr_2d, 2).and_then(lambda row: get_from(row, 0)) == Option.none()
            ```
        """
        ...

    @abstractmethod
    def flatmap(self, func: Callable[[KT], "Option[U]"]) -> "Option[U]":
        """Alias of [`and_then`][monad_std.option.Option.and_then]."""
        return self.and_then(func)

    @abstractmethod
    def bool_or(self, optb: "Option[KT]") -> "Option[KT]":
        """Returns the option if it contains a value, otherwise returns `optb`. Alias `||(__or__)`.

        `or` is a keyword in Python, so here we use `bool_or` instead.

        Arguments passed to or are eagerly evaluated.<br />
        If you are passing the result of a function call,
        it is recommended to use [`or_else`][monad_std.option.Option.or_else], which is lazily evaluated.

        Args:
            optb: Another option object to do the bool evaluation.

        Examples:
            ```python
            assert Option.some(2).bool_or(Option.none()) == Option.some(2)
            assert Option.none().bool_or(Option.some(100)) == Option.some(100)
            assert Option.some(2).bool_or(Option.some(100)) == Option.some(2)
            assert Option.none().bool_or(Option.none()) == Option.none()
            ```
        """
        ...

    @abstractmethod
    def or_else(self, func: Callable[[], "Option[KT]"]) -> "Option[KT]":
        """Returns the option if it contains a value, otherwise calls `func` and returns the result.

        Args:
            func: A callable object to produce the next value.

        Examples:
            ```python
            assert Option.some('foo').or_else(lambda: Option.some('bar')) == Option.some('foo')
            assert Option.none().or_else(lambda: Option.some('bar')) == Option.some('bar')
            assert Option.none().or_else(lambda: Option.none()) == Option.none()
            ```
        """
        ...

    @abstractmethod
    def bool_xor(self, optb: "Option[KT]") -> "Option[KT]":
        """Returns `Some` if exactly one of `self`, `optb` is `Some`, otherwise returns `None`. Alias `^(__xor__)`.

        Args:
            optb: Another option object to do the bool evaluation.

        Examples:
            ```python
            assert Option.some(2).bool_xor(Option.none()) == Option.some(2)
            assert Option.none().bool_xor(Option.some(2)) == Option.some(2)
            assert Option.some(2).bool_xor(Option.some(2)) == Option.none()
            assert Option.none().bool_xor(Option.none()) == Option.none()
            ```
        """
        ...

    @abstractmethod
    def filter(self, func: Callable[[KT], bool]) -> "Option[KT]":
        """Filter the option.

        Returns `None` if the option is `None`, otherwise calls predicate with the wrapped value and returns:

        - `Some(t)` if predicate returns `True` (where `t` is the wrapped value), and
        - `None` if predicate returns `False`.

        This function works similar to `builtin.filter()`.
        You can imagine the `Option<KT>` being an iterator over one or zero elements.
        `filter()` lets you decide which elements to keep.

        Args:
            func: The callable object decides whether the element should be kept.

        Examples:
            ```python
            assert Option.none().filter(lambda n: n % 2 == 0) == Option.none()
            assert Option.some(3).filter(lambda n: n % 2 == 0) == Option.none()
            assert Option.some(4).filter(lambda n: n % 2 == 0) == Option.some(4)
            ```
        """
        ...

    @abstractmethod
    def zip(self, other: "Option[U]") -> "Option[Tuple[KT, U]]":
        """Zips `self` with another `Option`.

        If `self` is `Some(s)` and `other` is `Some(o)`, this method returns `Some((s, o))`.
        Otherwise, `None` is returned.

        Examples:
            ```python
            assert Option.some(1).zip(Option.some('hi')) == Option.some((1, 'hi'))
            assert Option.some(1).zip(Option.none()) == Option.none()
            ```
        """
        ...

    @abstractmethod
    def zip_with(self, other: "Option[U]", func: Callable[["Option[KT]", "Option[U]"], "Option[R]"]) -> "Option[R]":
        """Zips `self` and another `Option` with a callable object.

        If self is `Some(s)` and other is `Some(o)`, this method returns `Some(f(s, o))`. Otherwise, `None` is returned.

        Examples:
            ```python
            def make_point(x, y):
                return Option.some({"x": x, "y": y})

            assert Option.some(2)
                .zip_with(Option.some(4), lambda x: make_point(*x)) == Option.some({ "x": 2, "y": 4})
            assert Option.some(2).zip_with(Option.none(), lambda x: make_point(*x)) == Option.none()
            ```
        """
        ...

    @abstractmethod
    def clone(self) -> "Option[KT]":
        """Clone self."""
        ...

    @staticmethod
    def clone_from(value: "Option[KT]") -> "Option[KT]":
        """Clone an `Option`."""
        return value.clone()

    def unzip(self: "Option[Tuple[T, U]]") -> Tuple["Option[T]", "Option[U]"]:
        """ Unzips an option containing a tuple of two options.

        If self is `Some((a, b))` this method returns `(Some(a), Some(b))`. Otherwise, `(None, None)` is returned.

        Examples:
            ```python
            assert Option.some((1, 'hi')).unzip() == (Option.some(1), Option.some('hi'))
            assert Option.none().unzip() == (Option.none(), Option.none())
            ```
        """
        if self.is_some():
            uwp = self.unwrap()
            return Option.some(uwp[0]), Option.some(uwp[1])
        else:
            return OpNone(), OpNone()

    def transpose(self: "Option[Result[T, E]]") -> "Result[Option[T], E]":
        """Transposes an `Option` of a [`Result`][monad_std.result.Result] into a `Result` of an `Option`.

        `None` will be mapped to `Ok(None)`.
        `Some(Ok(_))` and `Some(Err(_))` will be mapped to `Ok(Some(_))` and `Err(_)`.

        Examples:
            ```python
            x = Result.of_ok(Option.some(5))
            y = Option.some(Result.of_ok(5))
            assert x == y.transpose()
            ```
        """
        if self.is_none():
            return Result.of_ok(OpNone())
        elif self.unwrap().is_ok():
            return Result.of_ok(Option.some(self.unwrap().unwrap()))
        else:
            return Result.of_err(self.unwrap().unwrap_err())

    def flatten(self: "Option[Option[KT]]") -> "Option[KT]":
        """Converts from `Option<Option<KT>>` to `Option<KT>`.

        Examples:
            ```python
            assert Option.some(Option.some(6)).flatten() == Option.some(6)
            assert Option.some(Option.none()).flatten() == Option.none()
            assert Option.none().flatten() == Option.none()
            ```
            Flattening only removes one level of nesting at a time:
            ```python
            assert (Option.some(Option.some(Option.some(6))).flatten()
                == Option.some(Option.some(6)))
            assert (Option.some(Option.some(Option.some(6))).flatten().flatten()
                == Option.some(6))
            ```
        """
        if self.is_some() and self.unwrap().is_some():
            return Option.some(self.unwrap().unwrap())
        else:
            return OpNone()


class OpSome(Generic[KT], Option[KT]):
    __value: KT

    def __init__(self, __value: KT):
        self.__value = __value

    def __bool__(self):
        return True

    def __str__(self):
        return str(self.__value)

    def __repr__(self):
        return f'Option::Some({self.__value})'

    def __eq__(self, other):
        if isinstance(other, OpSome):
            return self.__value == other.__value
        else:
            return False

    def __hash__(self):
        return hash(self.__value)

    def clone(self):
        return OpSome(self.__value)

    def is_some(self) -> bool:
        return True

    def is_none(self) -> bool:
        return False

    def is_some_and(self, func: Callable[[KT], bool]) -> bool:
        return func(self.__value)

    def expect(self, msg: str) -> KT:
        return self.__value

    def to_nullable(self) -> Optional[KT]:
        return self.__value

    def unwrap(self) -> KT:
        return self.__value

    def unwrap_or(self, default: KT) -> KT:
        return self.__value

    def unwrap_or_else(self, func: Callable[[], KT]) -> KT:
        return self.__value

    def unwrap_unchecked(self) -> Optional[KT]:
        return self.__value

    def to_pattern(self) -> Optional[KT]:
        return self.__value

    def inspect(self, func: Callable[[KT], None]) -> Option[KT]:
        func(self.__value)
        return self

    def map(self, func: Callable[[KT], U]) -> Option[U]:
        return Option.some(func(self.__value))

    def map_mut(self, func: Callable[[KT], None]) -> Option[KT]:
        func(self.__value)
        return self

    def map_or(self, default: U, func: Callable[[KT], U]) -> U:
        return func(self.__value)

    def map_or_else(self, default: Callable[[], U], func: Callable[[KT], U]) -> U:
        return func(self.__value)

    def ok_or(self, err: E) -> "Result[KT, E]":
        return Result.of_ok(self.__value)

    def ok_or_else(self, err: Callable[[], E]) -> "Result[KT, E]":
        return Result.of_ok(self.__value)

    def to_array(self) -> List[KT]:
        return [self.__value]

    def bool_and(self, optb: Option[U]) -> Option[U]:
        return optb.clone()

    def and_then(self, func: Callable[[KT], Option[U]]) -> Option[U]:
        return func(self.__value)

    def flatmap(self, func: Callable[[KT], Option[U]]) -> Option[U]:
        return func(self.__value)

    def bool_or(self, optb: Option[KT]) -> Option[KT]:
        return self.clone()

    def or_else(self, func: Callable[[], Option[KT]]) -> Option[KT]:
        return self.clone()

    def bool_xor(self, optb: Option[KT]) -> Option[KT]:
        if optb.is_some():
            return OpNone()
        else:
            return self.clone()

    def filter(self, func: Callable[[KT], bool]) -> Option[KT]:
        if func(self.__value):
            return self.clone()
        else:
            return OpNone()

    def zip(self, other: Option[U]) -> Option[Tuple[KT, U]]:
        if other.is_some():
            return OpSome((self.__value, other.unwrap()))
        else:
            return OpNone()

    def zip_with(self, other: Option[U], func: Callable[[Option[KT], Option[U]], Option[R]]) -> Option[R]:
        if other.is_some():
            return func(self.__value, other.unwrap())
        else:
            return OpNone()


class OpNone(Generic[KT], Option[KT]):
    def __bool__(self):
        return False

    def __str__(self):
        return 'None'

    def __repr__(self):
        return 'Option::None'

    def __eq__(self, other):
        return isinstance(other, OpNone)

    def __hash__(self):
        return hash(None)

    def clone(self):
        return self

    def is_some(self) -> bool:
        return False

    def is_none(self) -> bool:
        return True

    def is_some_and(self, func: Callable[[KT], bool]) -> bool:
        return False

    def expect(self, msg: str) -> KT:
        raise UnwrapException("Option", msg)

    def to_nullable(self) -> Optional[KT]:
        return None

    def unwrap(self) -> KT:
        raise UnwrapException("Option", "call `Option.unwrap` on an `Option::None` object")

    def unwrap_or(self, default: KT) -> KT:
        return default

    def unwrap_or_else(self, func: Callable[[], KT]) -> KT:
        return func()

    def unwrap_unchecked(self) -> Optional[KT]:
        return None

    def to_pattern(self) -> Optional[KT]:
        return None

    def inspect(self, func: Callable[[KT], None]) -> Option[KT]:
        return self

    def map(self, func: Callable[[KT], U]) -> Option[U]:
        return self

    def map_mut(self, func: Callable[[KT], None]) -> Option[KT]:
        return self

    def map_or(self, default: U, func: Callable[[KT], U]) -> U:
        return default

    def map_or_else(self, default: Callable[[], U], func: Callable[[KT], U]) -> U:
        return default()

    def ok_or(self, err: E) -> "Result[KT, E]":
        return Result.of_err(err)

    def ok_or_else(self, err: Callable[[], E]) -> "Result[KT, E]":
        return Result.of_err(err())

    def to_array(self) -> List[KT]:
        return []

    def bool_and(self, optb: Option[U]) -> Option[U]:
        return self

    def and_then(self, func: Callable[[KT], Option[U]]) -> Option[U]:
        return self

    def flatmap(self, func: Callable[[KT], Option[U]]) -> Option[U]:
        return self

    def bool_or(self, optb: Option[KT]) -> Option[KT]:
        return optb.clone()

    def or_else(self, func: Callable[[], Option[KT]]) -> Option[KT]:
        return func()

    def bool_xor(self, optb: Option[KT]) -> Option[KT]:
        return optb.clone()

    def filter(self, func: Callable[[KT], bool]) -> Option[KT]:
        return self

    def zip(self, other: Option[U]) -> Option[Tuple[KT, U]]:
        return self

    def zip_with(self, other: Option[U], func: Callable[[Option[KT], Option[U]], Option[R]]) -> Option[R]:
        return self


from .result import Result
