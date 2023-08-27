from typing import Generic, TypeVar, Optional, Callable, List, Tuple

from .error import UnwrapException

KT = TypeVar('KT')
T = TypeVar('T')
U = TypeVar('U')
E = TypeVar('E')
R = TypeVar('R')


class Option(Generic[KT]):
    """`Option` monad for python."""
    __value: Optional[KT]

    def __init__(self, value: Optional[KT]):
        self.__value = value

    def __bool__(self):
        """Returns `False` only if contained value is `None`."""
        return self.__value is not None

    def __str__(self):
        if self.__value is None:
            return "None"
        else:
            return str(self.__value)

    def __repr__(self):
        if self.__value is None:
            return "Option::None"
        else:
            return f"Option::Some({self.__value})"

    def __eq__(self, other):
        if isinstance(other, Option):
            if self.__value is None and other.__value is None:
                return True
            elif self.__value == other.__value:
                return True
            else:
                return False
        elif other is None:
            return self.__value is None
        else:
            return False

    def __and__(self, other):
        return self.bool_and(other)

    def __or__(self, other):
        return self.bool_or(other)

    def __xor__(self, other):
        return self.bool_xor(other)

    @staticmethod
    def of_some(value: KT) -> "Option[KT]":
        """ Create a value of `Some(KT)`.

        Args:
            value: Some value of type `KT`.

        Returns:
            `Option::Some(KT)`
        """
        return Option(value)

    @staticmethod
    def of_none() -> "Option[KT]":
        """ Create a value of `None`.

        Returns:
            `Option::None`
        """
        return Option(None)

    def is_some(self) -> bool:
        """Returns `True` if the option is a `Some` value.

        Returns:
            Whether the option is a `Some` value.

        Examples:
            ```python
            x: Option[int] = Option.of_some(2)
            assert x.is_some()
            x: Option[int] = Option.of_none()
            assert not x.is_some()
            ```
        """
        return self.__value is not None

    def is_none(self) -> bool:
        """Returns `True` if the option is a `None` value.

        Returns:
            Whether the option is a `None` value.

        Examples:
            ```python
            x: Option[int] = Option.of_some(2)
            assert not x.is_none()
            x: Option[int] = Option.of_none()
            assert x.is_none()
            ```
        """
        return self.__value is None

    def is_some_and(self, func: Callable[[KT], bool]) -> bool:
        """Returns true if the option is a `Some` and the value inside it matches a predicate.

        Args:
            func: A callable object which accepts the *not-none* value of the option and returns a boolean.

        Returns:
            Whether the option is a `Some` and the value inside it matches a predicate.

        Examples:
            ```python
            x: Option[int] = Option.of_some(2)
            assert x.is_some_and(lambda v: v > 1)
            x: Option[int] = Option.of_some(0)
            assert not x.is_some_and(lambda v: v > 1)
            x: Option[int] = Option.of_none()
            assert not x.is_some_and(lambda v: v > 1)
            ```
        """
        return self.__value is not None and func(self.__value)

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
            x: Option[str] = Option.of_some('value')
            assert x.expect('hey, this is an `Option::None` object') == 'value'
            x: Option[str] = Option.of_none()
            try:
                x.expect('hey, this is an `Option::None` object')
            except UnwrapException as e:
                assert str(e) == 'hey, this is an `Option::None` object'
            ```
        """
        if self.__value is not None:
            return self.__value
        else:
            raise UnwrapException("Option", msg)

    def unwrap(self) -> KT:
        """Returns the contained `Some` value.

        Returns:
            The wrapped `Some` value.

        Raises:
            error.UnwrapException: Raise an exception if the value is a `None`.

        Examples:
            ```python
            x: Option[str] = Option.of_some("air")
            assert x.unwrap() == "air"
            x: Option[str] = Option.of_none()
            try:
                x.unwrap()
            except UnwrapException as e:
                assert str(e) == 'OptionError: call `Option.unwrap` on an `Option::None` object'
            ```
        """
        if self.__value is not None:
            return self.__value
        else:
            raise UnwrapException("Option", "call `Option.unwrap` on an `Option::None` object")

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
            assert Option.of_some("car").unwrap_or("bike") == "car"
            assert Option.of_none().unwrap_or("bike") == "bike"
            ```
        """
        if self.__value is not None:
            return self.__value
        else:
            return default

    def unwrap_or_else(self, func: Callable[[], KT]) -> KT:
        """Returns the contained `Some` value or computes it from a callable object.

        Args:
            func: A callable object to compute.

        Examples:
            ```python
            k = 10
            assert Option.of_some(4).unwrap_or_else(lambda: 2 * k) == 4
            assert Option.of_none().unwrap_or_else(lambda: 2 * k) == 20
            ```
        """
        if self.__value is not None:
            return self.__value
        else:
            return func()

    def unwrap_unchecked(self) -> Optional[KT]:
        """Returns the contained `Some` value, without checking that the value is not `None`."""
        return self.__value

    def inspect(self, func: Callable[[KT], None]) -> "Option[KT]":
        """Calls the provided closure with the contained value (if `Some`), and return the option itself.

        Args:
            func: A callable object which accepts the wrapped value and returns nothing.

        Examples:
            ```python
            x = []
            Option.of_some(2).inspect(lambda s: x.append(s))
            assert x == [2]
            Option.of_none().inspect(lambda s: x.append(s))
            assert x == [2]
            ```
        """
        if self.__value is not None:
            func(self.__value)
        return self

    def map(self, func: Callable[[KT], U]) -> "Option[U]":
        """Maps an `Option<KT>` to `Option<U>` by applying a function
        to a contained value (if `Some`) or returns `None` (if `None`).

        Args:
            func: A callable object that accepts the wrapped value and returns the processed value.

        Returns:
            Returns `Option::Some(U)` if the option is `Some` and returns `None` otherwise.

        Examples:
            ```python
            maybe_some_string = Option.of_some("Hello, World!")
            # `Option::map` will create a new option object
            maybe_some_len = maybe_some_string.map(lambda s: len(s))
            assert maybe_some_len == Option.of_some(13)
            assert Option.of_none().map(lambda s: len(s)) == Option.of_none()
            ```
        """
        if self.__value is not None:
            return Option.of_some(func(self.__value))
        else:
            return Option.of_none()

    def map_or(self, default: U, func: Callable[[KT], U]) -> U:
        """Returns the provided default result (if none), or applies a function to the contained value (if any).

        Arguments passed to map_or are eagerly evaluated.<br />If you are passing the result of a function call,
        it is recommended to use [`map_or_else`][monad_std.option.Option.map_or_else], which is lazily evaluated.

        Args:
            default: The default value if the option is `None`.
            func: The function to apply to the contained value.

        Examples:
            ```python
            assert Option.of_some('foo').map_or(42, lambda s: len(s)) == 3
            assert Option.of_none().map_or(42, lambda s: len(s)) == 42
            ```
        """
        if self.__value is not None:
            return func(self.__value)
        else:
            return default

    def map_or_else(self, default: Callable[[], U], func: Callable[[KT], U]) -> U:
        """Computes a default function result (if none),
        or applies a different function to the contained value (if any).

        Args:
            default: The function to produce a default value.
            func: The function to apply to the contained value.

        Examples:
            ```python
            k = 21
            assert Option.of_some('bar').map_or_else(lambda: 2 * k, lambda s: len(s)) == 3
            assert Option.of_none().map_or_else(lambda: 2 * k, lambda s: len(s)) == 42
            ```
        """
        if self.__value is not None:
            return func(self.__value)
        else:
            return default()

    def ok_or(self, err: E) -> "Result[KT, E]":
        """Transforms the `Option<KT>` into a `Result<KT, E>`, mapping `Some(v)` to `Ok(v)` and `None` to `Err(err)`.

        Arguments passed to ok_or are eagerly evaluated.<br />
        If you are passing the result of a function call,
        it is recommended to use [`ok_or_else`][monad_std.option.Option.ok_or_else], which is lazily evaluated.

        Args:
            err: A value representing an error

        Examples:
            ```python
            assert Option.of_some('foo').ok_or(0) == Result.of_ok('foo')
            assert Option.of_none().ok_or(0) == Result.of_err(0)
            ```
        """
        if self.__value is not None:
            return Result.of_ok(self.__value)
        else:
            return Result.of_err(err)

    def ok_or_else(self, err: Callable[[], E]) -> "Result[KT, E]":
        """Transforms the `Option<KT>` into a `Result<KT, E>`, mapping `Some(v)` to `Ok(v)` and `None` to `Err(err())`.

        Args:
            err: A callable object that returns an error value.

        Examples:
            ```python
            k = 21
            assert Option.of_some('foo').ok_or_else(lambda: k * 2) == Result.of_ok('foo')
            assert Option.of_none().ok_or_else(lambda: k * 2) == Result.of_err(42)
            ```
        """
        if self.__value is not None:
            return Result.of_ok(self.__value)
        else:
            return Result.of_err(err())

    def to_array(self) -> List[KT]:
        """Returns an array of the possible contained value.

        Examples:
            ```python
            assert Option.of_some(1).to_array() == [1]
            assert Option.of_none().to_array() == []
            ```
        """
        v = []
        if self.__value is not None:
            v.append(self.__value)
        return v

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
            assert Option.of_some(2).bool_and(Option.of_none()) == Option.of_none()
            assert Option.of_none().bool_and(Option.of_some('foo')) == Option.of_none()
            assert Option.of_some(2).bool_and(Option.of_some('bar')) == Option.of_some('bar')
            assert Option.of_none().bool_and(Option.of_none()) == Option.of_none()
            ```
        """
        if self.__value is None:
            return Option.of_none()
        elif optb.__value is not None:
            return Option.of_some(optb.__value)
        else:
            return Option.of_none()

    def and_then(self, func: Callable[[KT], "Option[U]"]) -> "Option[U]":
        """Returns `None` if the option is `None`,
        otherwise calls `func` with the wrapped value and returns the result. Alias `flatmap`.

        Args:
            func: A callable object to produce the next value.

        Examples:
            ```python
            assert Option.of_some(2).and_then(lambda x: Option.of_some(str(x))) == Option.of_some('2')
            assert Option.of_some(10).and_then(lambda _: Option.of_none()) == Option.of_none()
            assert Option.of_none().and_then(lambda x: Option.of_some(str(x))) == Option.of_none()
            ```
            Often used to chain fallible operations that may return `None`.
            ```python
            def get_from(l, i):
                try:
                    return Option.of_some(l[i])
                except IndexError:
                    return Option.of_none()

            arr2d = [["A0", "A1"], ["B0", "B1"]]
            assert get_from(arr2d, 0).and_then(lambda row: get_from(row, 1)) == Option.of_some('A1')
            assert get_from(arr2d, 2).and_then(lambda row: get_from(row, 0)) == Option.of_none()
            ```
        """
        if self.__value is None:
            return Option.of_none()
        else:
            return func(self.__value)

    def flatmap(self, func: Callable[[KT], "Option[U]"]) -> "Option[U]":
        """Alias of [`and_then`][monad_std.option.Option.and_then]."""
        return self.and_then(func)

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
            assert Option.of_some(2).bool_or(Option.of_none()) == Option.of_some(2)
            assert Option.of_none().bool_or(Option.of_some(100)) == Option.of_some(100)
            assert Option.of_some(2).bool_or(Option.of_some(100)) == Option.of_some(2)
            assert Option.of_none().bool_or(Option.of_none()) == Option.of_none()
            ```
        """
        if self.__value is None:
            if optb.__value is None:
                return Option.of_none()
            else:
                return Option.of_some(optb.__value)
        else:
            return Option.of_some(self.__value)

    def or_else(self, func: Callable[[], "Option[KT]"]) -> "Option[KT]":
        """Returns the option if it contains a value, otherwise calls `func` and returns the result.

        Args:
            func: A callable object to produce the next value.

        Examples:
            ```python
            assert Option.of_some('foo').or_else(lambda: Option.of_some('bar')) == Option.of_some('foo')
            assert Option.of_none().or_else(lambda: Option.of_some('bar')) == Option.of_some('bar')
            assert Option.of_none().or_else(lambda: Option.of_none()) == Option.of_none()
            ```
        """
        if self.__value is None:
            return func()
        else:
            return Option.of_some(self.__value)

    def bool_xor(self, optb: "Option[KT]") -> "Option[KT]":
        """Returns `Some` if exactly one of `self`, `optb` is `Some`, otherwise returns `None`. Alias `^(__xor__)`.

        Args:
            optb: Another option object to do the bool evaluation.

        Examples:
            ```python
            assert Option.of_some(2).bool_xor(Option.of_none()) == Option.of_some(2)
            assert Option.of_none().bool_xor(Option.of_some(2)) == Option.of_some(2)
            assert Option.of_some(2).bool_xor(Option.of_some(2)) == Option.of_none()
            assert Option.of_none().bool_xor(Option.of_none()) == Option.of_none()
            ```
        """
        if self.__value is None and optb.__value is not None:
            return Option.of_some(optb.__value)
        elif self.__value is not None and optb.__value is None:
            return Option.of_some(self.__value)
        else:
            return Option.of_none()

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
            assert Option.of_none().filter(lambda n: n % 2 == 0) == Option.of_none()
            assert Option.of_some(3).filter(lambda n: n % 2 == 0) == Option.of_none()
            assert Option.of_some(4).filter(lambda n: n % 2 == 0) == Option.of_some(4)
            ```
        """
        if self.__value is not None and func(self.__value):
            return Option.of_some(self.__value)
        else:
            return Option.of_none()

    def zip(self, other: "Option[U]") -> "Option[Tuple[KT, U]]":
        """Zips `self` with another `Option`.

        If `self` is `Some(s)` and `other` is `Some(o)`, this method returns `Some((s, o))`.
        Otherwise, `None` is returned.

        Examples:
            ```python
            assert Option.of_some(1).zip(Option.of_some('hi')) == Option.of_some((1, 'hi'))
            assert Option.of_some(1).zip(Option.of_none()) == Option.of_none()
            ```
        """
        if self.__value is not None and other.__value is not None:
            return Option.of_some((self.__value, other.__value))
        else:
            return Option.of_none()

    def zip_with(self, other: "Option[U]", func: Callable[["Option[KT]", "Option[U]"], "Option[R]"]) -> "Option[R]":
        """Zips `self` and another `Option` with a callable object.

        If self is `Some(s)` and other is `Some(o)`, this method returns `Some(f(s, o))`. Otherwise, `None` is returned.

        Examples:
            ```python
            def make_point(x, y):
                return Option.of_some({"x": x, "y": y})

            assert Option.of_some(2)
                .zip_with(Option.of_some(4), lambda x: make_point(*x)) == Option.of_some({ "x": 2, "y": 4})
            assert Option.of_some(2).zip_with(Option.of_none(), lambda x: make_point(*x)) == Option.of_none()
            ```
        """
        if self.__value is not None and other.__value is not None:
            return func(self.__value, other.__value)
        else:
            return Option.of_none()

    @staticmethod
    def unzip(opt: "Option[Tuple[T, U]]") -> Tuple["Option[T]", "Option[U]"]:
        """ Unzips an option containing a tuple of two options.

        If self is `Some((a, b))` this method returns `(Some(a), Some(b))`. Otherwise, `(None, None)` is returned.

        Args:
            opt: Option to unzip.

        Examples:
            ```python
            assert Option.unzip(Option.of_some((1, 'hi'))) == (Option.of_some(1), Option.of_some('hi'))
            assert Option.unzip(Option.of_none()) == (Option.of_none(), Option.of_none())
            ```
        """
        if opt.__value is not None:
            return Option.of_some(opt.__value[0]), Option.of_some(opt.__value[1])
        else:
            return Option.of_none(), Option.of_none()

    @staticmethod
    def transpose(opt: "Option[Result[T, E]]") -> "Result[Option[T], E]":
        """Transposes an `Option` of a [`Result`][monad_std.result.Result] into a `Result` of an `Option`.

        `None` will be mapped to `Ok(None)`.
        `Some(Ok(_))` and `Some(Err(_))` will be mapped to `Ok(Some(_))` and `Err(_)`.

        Args:
            opt: Option to be transposed

        Examples:
            ```python
            x = Result.of_ok(Option.of_some(5))
            y = Option.of_some(Result.of_ok(5))
            assert x == Option.transpose(y)
            ```
        """
        if opt.__value is None:
            return Result.of_ok(Option.of_none())
        elif opt.__value.is_ok():
            return Result.of_ok(Option.of_some(opt.__value.unwrap()))
        else:
            return Result.of_err(opt.__value.unwrap_err())

    @staticmethod
    def flatten(opt: "Option[Option[T]]") -> "Option[T]":
        """Converts from `Option<Option<KT>>` to `Option<KT>`.

        Args:
            opt: Option to flatten.

        Examples:
            ```python
            assert Option.flatten(Option.of_some(Option.of_some(6))) == Option.of_some(6)
            assert Option.flatten(Option.of_some(Option.of_none())) == Option.of_none()
            assert Option.flatten(Option.of_none()) == Option.of_none()
            ```
            Flattening only removes one level of nesting at a time:
            ```python
            assert (Option.flatten(Option.of_some(Option.of_some(Option.of_some(6))))
                == Option.of_some(Option.of_some(6)))
            assert (Option.flatten(Option.flatten(Option.of_some(Option.of_some(Option.of_some(6)))))
                == Option.of_some(6))
            ```
        """
        if opt.__value is not None and opt.__value.__value is not None:
            return Option.of_some(opt.__value.__value)
        else:
            return Option.of_none()


from .result import Result
