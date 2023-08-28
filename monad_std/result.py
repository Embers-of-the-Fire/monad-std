from typing import Generic, TypeVar, Callable, List, Any, Iterator
from abc import ABCMeta, abstractmethod

from .error import UnwrapException

KT = TypeVar('KT')
KE = TypeVar('KE')
T = TypeVar('T')
E = TypeVar('E')
U = TypeVar('U')
F = TypeVar('F')


class Result(Generic[KT, KE], metaclass=ABCMeta):
    """An ancestor class of any `Result` type, inherited by `Ok` and `Err` subclasses."""

    @staticmethod
    def of_ok(value: KT) -> "Result[KT, KE]":
        """Create an `Ok` value."""
        return Ok(value)

    @staticmethod
    def of_err(value: KE) -> "Result[KT, KE]":
        """Create an `Err` value."""
        return Err(value)

    @staticmethod
    def catch(func: Callable[[], T]) -> "Result[T, Exception]":
        """Catch a thrown exception from the function.

        Args:
            func: A function to catch the thrown exception.

        Returns:
            A `Result` of either the result of the function or the exception. You can cast the exception manually.

        Examples:
            ```python
            def maybe_error(v: int) -> int:
                if v % 2 == 0:
                    return v + 1
                else:
                    raise ValueError()

            assert Result.catch(lambda: maybe_error(2)) == Result.of_ok(3)
            assert isinstance(Result.catch(lambda: maybe_error(3)).unwrap_err(), ValueError)
            ```
        """
        try:
            return Result.of_ok(func())
        except Exception as e:
            return Result.of_err(e)

    @staticmethod
    def catch_from(func: Callable, *args: Any, **kwargs: Any) -> "Result":
        """Catch a thrown exception from a function call.

        Args:
            func: The function to call
            *args: The arguments passing to `func`.
            **kwargs: The keyword arguments passing to `func`.

        Returns:
            A `Result` of either the result of the function or the exception. You can cast them manually.

        Examples:
            ```python
            def maybe_error(v: int) -> int:
                if v % 2 == 0:
                    return v + 1
                else:
                    raise ValueError()

            assert Result.catch_from(maybe_error, v=2) == Result.of_ok(3)
            assert isinstance(Result.catch_from(maybe_error, 3).unwrap_err(), ValueError)
            ```
        """
        try:
            return Result.of_ok(func(*args, **kwargs))
        except Exception as e:
            return Result.of_err(e)

    def __bool__(self):
        """Returns `True` if the result is `Ok`."""
        return self.is_ok()

    @abstractmethod
    def __repr__(self):
        ...

    @abstractmethod
    def __str__(self):
        ...

    @abstractmethod
    def __eq__(self, other):
        ...

    def __add__(self, other):
        """Alias `self.__value.__add__`.

        Returns:
            If both value are `Ok`, this will return `Ok(self + other)`. Otherwise, return the first `Err`.
        """
        if isinstance(other, Result):
            if self.is_ok():
                return other.map(lambda x: x + self.unwrap())
            else:
                return Result.of_err(self.unwrap_err())
        else:
            raise TypeError("expect a Result type")

    def __mul__(self, other):
        """Alias `self.__value.__mul__`.

        Returns:
            If both value are `Ok`, this will return `Ok(self * other)`. Otherwise, return the first `Err`.
        """
        if isinstance(other, Result):
            if self.is_ok():
                return other.map(lambda x: x * self.unwrap())
            else:
                return Result.of_err(self.unwrap_err())
        else:
            raise TypeError("expect a Result type")

    def __iter__(self) -> Iterator[KT]:
        return iter(self.to_array())

    def to_iter(self) -> Iterator[KT]:
        """Alias `iter(self.to_array())`."""
        return iter(self.to_array())

    def __and__(self, other):
        if isinstance(other, Result):
            return self.bool_and(other)
        else:
            raise TypeError("expect a Result type")

    def __or__(self, other):
        if isinstance(other, Result):
            return self.bool_or(other)
        else:
            raise TypeError("expect a Result type")

    def __instancecheck__(self, instance):
        return isinstance(instance, (Ok, Err))

    @abstractmethod
    def is_ok(self) -> bool:
        """Returns `True` if the result is `Ok`.

        Examples:
            ```python
            assert Result.of_ok(2).is_ok()
            assert not Result.of_err('err').is_ok()
            ```
        """
        ...

    @abstractmethod
    def is_ok_and(self, func: Callable[[KT], bool]) -> bool:
        """Returns `True` if the result is `Ok` and the value inside it matches a predicate.

        Args:
            func: The predicate function.

        Examples:
            ```python
            assert Result.of_ok(2).is_ok_and(lambda x: x > 1)
            assert not Result.of_ok(0).is_ok_and(lambda x: x > 1)
            assert not Result.of_err('error').is_ok_and(lambda x: x > 1)
            ```
        """
        ...

    @abstractmethod
    def is_err(self) -> bool:
        """Returns `True` if the result is `Err`.

        Examples:
            ```python
            assert not Result.of_ok(2).is_err()
            assert Result.of_err('err').is_err()
            ```
        """
        ...

    @abstractmethod
    def is_err_and(self, func: Callable[[KE], bool]) -> bool:
        """Returns `True` if the result is `Err`.

        Args:
            func: The predicate function.

        Examples:
            ```python
            assert not Result.of_ok(2).is_err_and(lambda x: len(x) == 3)
            assert Result.of_err('err').is_err_and(lambda x: len(x) == 3)
            assert not Result.of_err('error').is_err_and(lambda x: len(x) == 3)
            ```
        """
        ...

    @abstractmethod
    def ok(self) -> "Option[KT]":
        """Converts from `Result<KT, KE>` to [`Option<KT>`][monad_std.option.Option].

        Converts `self` into an `Option<KT>`, and discarding the error, if any.

        Examples:
            ```python
            assert Result.of_ok(2).ok() == Option.of_some(2)
            assert Result.of_err('err').ok() == Option.of_none()
            ```
        """
        ...

    @abstractmethod
    def err(self) -> "Option[KE]":
        """Converts from `Result<KT, KE>` to [`Option<KE>`][monad_std.option.Option].

        Converts `self` into an `Option<KE>`, and discarding the success value, if any.

        Examples:
            ```python
            assert Result.of_err('err').err() == Option.of_some('err')
            assert Result.of_ok(0).err() == Option.of_none()
            ```
        """
        ...

    @abstractmethod
    def map(self, func: Callable[[KT], U]) -> "Result[U, KE]":
        """Maps a `Result<KT, KE>` to `Result<U, KE>` by applying a function to a contained `Ok` value,
        leaving an `Err` value untouched.

        This function can be used to compose the results of two functions.

        Examples:
            ```python
            assert Result.of_ok(2).map(lambda x: x * 2) == Result.of_ok(4)
            assert Result.of_err('err').map(lambda x: x * 2) == Result.of_err('err')
            ```
        """
        ...

    @abstractmethod
    def map_or(self, default: U, func: Callable[[KT], U]) -> U:
        """Returns the provided `default` (if `Err`), or applies a function to the contained value (if `Ok`).

        Arguments passed to `map_or` are eagerly evaluated.<br />
        If you are passing the result of a function call,
        it is recommended to use [`map_or_else`][monad_std.result.Result.map_or_else], which is lazily evaluated.

        Args:
            default: The default value.
            func: The function to apply to the result.

        Examples:
            ```python
            assert Result.of_ok('foo').map_or(42, lambda s: len(s)) == 3
            assert Result.of_err('bar').map_or(42, lambda s: len(s)) == 42
            ```
        """
        ...

    @abstractmethod
    def map_or_else(self, default: Callable[[KE], U], func: Callable[[KT], U]) -> U:
        """Maps a `Result<KT, KE>` to `U` by applying fallback function `default` to a contained `Err` value,
        or function `func` to a contained `Ok` value.

        This function can be used to unpack a successful result while handling an error.

        Args:
            default: The fallback function to produce a default value.
            func: The function to apply to the success value.

        Examples:
            ```python
            assert Result.of_ok('foo').map_or_else(lambda e: len(e) + 3, lambda v: len(v)) == 3
            assert Result.of_err('bar').map_or_else(lambda e: len(e) + 3, lambda v: len(v)) == 6
            ```
        """
        ...

    @abstractmethod
    def map_err(self, func: Callable[[KE], F]) -> "Result[KT, F]":
        """Maps a `Result<KT, KE>` to `Result<KT, F>` by applying a function to a contained `Err` value,
        leaving the `Ok` value untouched.

        Args:
            func: The function to apply to the `Err` value.

        Examples:
            ```python
            assert Result.of_ok(2).map_err(lambda x: str(x)) == Result.of_ok(2)
            assert Result.of_err(-1).map_err(lambda x: str(x)) == Result.of_err('-1')
            ```
        """
        ...

    @abstractmethod
    def inspect(self, func: Callable[[KT], None]) -> "Result[KT, KE]":
        """Calls the provided closure with a reference to the contained value (if `Ok`).

        Args:
            func: The closure to be executed.

        Examples:
            ```python
            k = []
            Result.of_ok(2).inspect(lambda x: k.append(x))
            assert k == [2]
            Result.of_err('err').inspect(lambda x: k.append(x))
            assert k == [2]
            ```
        """
        ...

    @abstractmethod
    def inspect_err(self, func: Callable[[KE], None]) -> "Result[KT, KE]":
        """Calls the provided closure with a reference to the contained value (if `Err`).

        Args:
            func: The closure to be executed.

        Examples:
            ```python
            k = []
            Result.of_ok(2).inspect_err(lambda x: k.append(x))
            assert k == []
            Result.of_err(-1).inspect_err(lambda x: k.append(x))
            assert k == [-1]
            ```
        """
        ...

    @abstractmethod
    def to_array(self) -> List[KT]:
        """Returns an array containing the possibly contained value.

        Examples:
            ```python
            assert Result.of_ok(2).to_array() == [2]
            assert Result.of_err('err').to_array() == []
            ```
        """
        ...

    @abstractmethod
    def expect(self, msg: str) -> KT:
        """Returns the contained `Ok` value.

        Because this function may raise an exception, its use is generally discouraged.
        Instead, prefer to call [`unwrap_or`][monad_std.result.Result.unwrap_or]
        or [`unwrap_or_else`][monad_std.result.Result.unwrap_or_else].

        **Recommended Message Style**
        We recommend that `expect` messages are used to describe the reason you expect the `Result` should be `Ok`.<br/>
        **Hint**:If you’re having trouble remembering how to phrase expect error messages remember
        to focus on the word “should” as in “env variable should be set by blah”
        or “the given binary should be available and executable by the current user”.

        Args:
            msg: The message of the exception.

        Raises:
            UnwrapException: Raises if the value is an `Err` with a message including the passed message and the `Err`.

        Examples:
            ```python
            assert Result.of_ok(2).expect('error') == 2
            try:
                Result.of_err('err').expect('error')
            except UnwrapException as e:
                assert str(e) == "ResultError: error: 'err'"
            ```
        """
        ...

    @abstractmethod
    def expect_err(self, msg: str) -> KE:
        """Returns the contained `Err` value.

        Args:
            msg: The message of the exception.

        Raises:
            UnwrapException: Raises if the value is an `Ok` with a message including the passed message and the `Ok`.

        Examples:
            ```python
            assert Result.of_err('err').expect_err('ok') == 'err'
            try:
                Result.of_ok(2).expect_err('ok')
            except UnwrapException as e:
                assert str(e) == "ResultError: ok: 2"
            ```
        """
        ...

    @abstractmethod
    def unwrap(self) -> KT:
        """Returns the contained `Ok` value.

        Because this function may raise an exception, its use is generally discouraged.
        Instead, prefer to call [`unwrap_or`][monad_std.result.Result.unwrap_or]
        or [`unwrap_or_else`][monad_std.result.Result.unwrap_or_else].

        Raises:
            UnwrapException: Raises if the value is an `Err`, with a panic message provided by the `Err`’s value.

        Examples:
            ```python
            assert Result.of_ok(2).unwrap() == 2
            try:
                Result.of_err('err').unwrap()
            except UnwrapException as e:
                assert str(e) == "ResultError: call `Result.unwrap` on an `Err` value: 'err'"
            ```
        """
        ...

    @abstractmethod
    def unwrap_or(self, default: KT) -> KT:
        """Returns the contained `Ok` value or a provided `default`.

        Arguments passed to unwrap_or are eagerly evaluated.<br />
        If you are passing the result of a function call,
        it is recommended to use [`unwrap_or_else`][monad_std.result.Result.unwrap_or_else], which is lazily evaluated.

        Args:
            default: The default value.

        Examples:
            ```python
            assert Result.of_ok(9).unwrap_or(2) == 9
            assert Result.of_err('err').unwrap_or(2) == 2
            ```
        """
        ...

    @abstractmethod
    def unwrap_or_else(self, op: Callable[[KE], KT]) -> KT:
        """Returns the contained `Ok` value or computes it from a closure.

        Args:
            op: The closure to compute.

        Examples:
            ```python
            assert Result.of_ok(2).unwrap_or_else(lambda s: len(s)) == 2
            assert Result.of_err('foo').unwrap_or_else(lambda s: len(s)) == 3
            ```
        """
        ...

    @abstractmethod
    def unwrap_err(self) -> KE:
        """Returns the contained `Err` value.

        Raises:
            UnwrapException: Raises if the value is an `Ok`, with a panic message provided by the `Ok`’s value.

        Examples:
            ```python
            assert Result.of_err('err').unwrap_err() == 'err'
            try:
                Result.of_ok(2).unwrap_err()
            except UnwrapException as e:
                assert str(e) == "ResultError: call `Result.unwrap_err` on an `Ok` value: 2"
            ```
        """
        ...

    @abstractmethod
    def bool_and(self, res: "Result[U, KE]") -> "Result[U, KE]":
        """Returns `res` if the result is `Ok`, otherwise returns the `Err` value of `self`. Alias `&(__and__)`.

        `and` is a keyword of Python, so we use `bool_and` instead.

        Arguments passed to and are eagerly evaluated.<br />
        If you are passing the result of a function call,
        it is recommended to use [`and_then`][monad_std.result.Result.and_then], which is lazily evaluated.

        Args:
            res: Another `Result` instance.

        Examples:
            ```python
            assert Result.of_ok(2).bool_and(Result.of_err('late error')) == Result.of_err('late error')
            assert Result.of_err('early error').bool_and(Result.of_ok(2)) == Result.of_err('early error')
            assert Result.of_err('early error').bool_and(Result.of_err('late error')) == Result.of_err('early error')
            assert Result.of_ok(2).bool_and(Result.of_ok('another ok')) == Result.of_ok('another ok')
            ```
        """
        ...

    @abstractmethod
    def and_then(self, op: Callable[[KT], "Result[U, KE]"]) -> "Result[U, KE]":
        """Calls `op` if the result is `Ok`, otherwise returns the `Err` value of `self`.

        This function can be used for control flow based on `Result` values.

        Args:
            op: The callable object to execute.

        Examples:
            ```python
            assert Result.of_ok(2).and_then(lambda n: Result.of_ok(n * 2)) == Result.of_ok(4)
            assert Result.of_ok(2).and_then(lambda _: Result.of_err('err')) == Result.of_err('err')
            assert Result.of_err('err').and_then(lambda n: Result.of_ok(n * 2)) == Result.of_err('err')
            ```
        """
        ...

    @abstractmethod
    def bool_or(self, res: "Result[KT, F]") -> "Result[KT, F]":
        """Returns `res` if the result is `Err`, otherwise returns the `Ok` value of `self`. Alias `||(__or__)`.

        `or` is a keyword of Python, so we use `bool_or` instead.

        Arguments passed to `or` are eagerly evaluated.<br />
        If you are passing the result of a function call,
        it is recommended to use [`or_else`][monad_std.result.Result.or_else], which is lazily evaluated.

        Args:
            res: Another `Result` instance.

        Examples:
            ```python
            assert Result.of_ok(2).bool_or(Result.of_err('late error')) == Result.of_ok(2)
            assert Result.of_err('early error').bool_or(Result.of_ok(2)) == Result.of_ok(2)
            assert Result.of_err('early error').bool_or(Result.of_err('late error')) == Result.of_err('late error')
            assert Result.of_ok(2).bool_or(Result.of_ok(100)) == Result.of_ok(2)
            ```
        """
        ...

    @abstractmethod
    def or_else(self, op: Callable[[KE], "Result[KT, F]"]) -> "Result[KT, F]":
        """Calls `op` if the result is `Err`, otherwise returns the `Ok` value of self.

        This function can be used for control flow based on result values.

        Args:
            op: The function to be executed.

        Examples:
            ```python
            def sq(x: int) -> Result[int, int]:
                return Result.of_ok(x * x)

            def err(x: int) -> Result[int, int]:
                return Result.of_err(x)

            assert Result.of_ok(2).or_else(sq).or_else(sq) == Result.of_ok(2)
            assert Result.of_ok(2).or_else(err).or_else(sq) == Result.of_ok(2)
            assert Result.of_err(3).or_else(sq).or_else(err) == Result.of_ok(9)
            assert Result.of_err(3).or_else(err).or_else(err) == Result.of_err(3)
            ```
        """
        ...

    @staticmethod
    def transpose(res: "Result[Option[T], E]") -> "Option[Result[T, E]]":
        """Transposes a `Result` of an `Option` into an `Option` of a `Result`.

        `Ok(None)` will be mapped to `None`.
        `Ok(Some(_))` and `Err(_)` will be mapped to `Some(Ok(_))` and `Some(Err(_))`.

        Examples:
            ```python
            x = Result.of_ok(Option.of_some(5))
            y = Option.of_some(Result.of_ok(5))
            assert Result.transpose(x) == y
            ```
        """
        if res.is_err():
            return Option.of_some(Result.of_err(res.unwrap_err()))
        else:
            return res.unwrap().map(Result.of_ok)

    @staticmethod
    def flatten(res: "Result[Result[T, E], E]") -> "Result[T, E]":
        """Converts from `Result<Result<T, E>, E>` to `Result<T, E>`.

        Examples:
            ```python
            assert Result.of_ok('hello') == Result.flatten(Result.of_ok(Result.of_ok('hello')))
            assert Result.of_err(6) == Result.flatten(Result.of_ok(Result.of_err(6)))
            assert Result.of_err(5) == Result.flatten(Result.of_err(5))
            ```
            Flattening only removes one level of nesting at a time:
            ```python
            x = Result.of_ok(Result.of_ok(Result.of_ok('hello')))
            assert Result.of_ok(Result.of_ok('hello')) == Result.flatten(x)
            assert Result.of_ok('hello') == Result.flatten(Result.flatten(x))
            ```
        """
        if res.is_err():
            return Result.of_err(res.unwrap_err())
        else:
            return res.unwrap()


class Ok(Generic[KT, KE], Result[KT, KE]):
    __value: KT

    def __init__(self, value: KT):
        self.__value = value

    def __repr__(self):
        return f"Result::Ok({self.__value})"

    def __str__(self):
        return str(self.__value)

    def __eq__(self, other):
        return isinstance(other, Ok) and self.__value == other.__value

    def __instancecheck__(self, instance):
        return isinstance(instance, Ok)

    def is_ok(self) -> bool:
        return True

    def is_ok_and(self, func: Callable[[KT], bool]) -> bool:
        return func(self.__value)

    def is_err(self) -> bool:
        return False

    def is_err_and(self, func: Callable[[KE], bool]) -> bool:
        return False

    def ok(self) -> "Option[KT]":
        return Option.of_some(self.__value)

    def err(self) -> "Option[KE]":
        return Option.of_none()

    def map(self, func: Callable[[KT], U]) -> Result[U, KE]:
        return Result.of_ok(func(self.__value))

    def map_or(self, default: U, func: Callable[[KT], U]) -> U:
        return func(self.__value)

    def map_or_else(self, default: Callable[[KE], U], func: Callable[[KT], U]) -> U:
        return func(self.__value)

    def map_err(self, func: Callable[[KE], F]) -> Result[KT, F]:
        return Result.of_ok(self.__value)

    def inspect(self, func: Callable[[KT], None]) -> Result[KT, KE]:
        func(self.__value)
        return self

    def inspect_err(self, func: Callable[[KE], None]) -> Result[KT, KE]:
        return self

    def to_array(self) -> List[KT]:
        return [self.__value]

    def expect(self, msg: str) -> KT:
        return self.__value

    def expect_err(self, msg: str) -> KE:
        raise UnwrapException("Result", msg + f': {repr(self.__value)}')

    def unwrap(self) -> KT:
        return self.__value

    def unwrap_or(self, default: KT) -> KT:
        return self.__value

    def unwrap_or_else(self, op: Callable[[KE], KT]) -> KT:
        return self.__value

    def unwrap_err(self) -> KE:
        raise UnwrapException("Result", f"call `Result.unwrap_err` on an `Ok` value: {self.__value}")

    def bool_and(self, res: Result[U, KE]) -> Result[U, KE]:
        if res.is_ok():
            return Result.of_ok(res.unwrap())
        elif res.is_err():
            return Result.of_err(res.unwrap_err())

    def and_then(self, op: Callable[[KT], Result[U, KE]]) -> Result[U, KE]:
        return op(self.__value)

    def bool_or(self, res: Result[KT, F]) -> Result[KT, F]:
        return Result.of_ok(self.__value)

    def or_else(self, op: Callable[[KE], Result[KT, F]]) -> Result[KT, F]:
        return Result.of_ok(self.__value)


class Err(Generic[KT, KE], Result[KT, KE]):
    __value: KE

    def __init__(self, value: KE):
        self.__value = value

    def __repr__(self):
        return f"Result::Err({self.__value})"

    def __str__(self):
        return str(self.__value)

    def __eq__(self, other):
        return isinstance(other, Err) and self.__value == other.__value

    def __instancecheck__(self, instance):
        return isinstance(instance, Err)

    def is_ok(self) -> bool:
        return False

    def is_ok_and(self, func: Callable[[KT], bool]) -> bool:
        return False

    def is_err(self) -> bool:
        return True

    def is_err_and(self, func: Callable[[KE], bool]) -> bool:
        return func(self.__value)

    def ok(self) -> "Option[KT]":
        return Option.of_none()

    def err(self) -> "Option[KE]":
        return Option.of_some(self.__value)

    def map(self, func: Callable[[KT], U]) -> Result[U, KE]:
        return Result.of_err(self.__value)

    def map_or(self, default: U, func: Callable[[KT], U]) -> U:
        return default

    def map_or_else(self, default: Callable[[KE], U], func: Callable[[KT], U]) -> U:
        return default(self.__value)

    def map_err(self, func: Callable[[KE], F]) -> Result[KT, F]:
        return Result.of_err(func(self.__value))

    def inspect(self, func: Callable[[KT], None]) -> Result[KT, KE]:
        return self

    def inspect_err(self, func: Callable[[KE], None]) -> Result[KT, KE]:
        func(self.__value)
        return self

    def to_array(self) -> List[KT]:
        return []

    def expect(self, msg: str) -> KT:
        raise UnwrapException("Result", msg + f': {repr(self.__value)}')

    def expect_err(self, msg: str) -> KE:
        return self.__value

    def unwrap(self) -> KT:
        raise UnwrapException("Result", f"call `Result.unwrap` on an `Err` value: {repr(self.__value)}")

    def unwrap_or(self, default: KT) -> KT:
        return default

    def unwrap_or_else(self, op: Callable[[KE], KT]) -> KT:
        return op(self.__value)

    def unwrap_err(self) -> KE:
        return self.__value

    def bool_and(self, res: Result[U, KE]) -> Result[U, KE]:
        return Result.of_err(self.__value)

    def and_then(self, op: Callable[[KT], Result[U, KE]]) -> Result[U, KE]:
        return Result.of_err(self.__value)

    def bool_or(self, res: Result[KT, F]) -> Result[KT, F]:
        if res.is_ok():
            return Result.of_ok(res.unwrap())
        else:
            return Result.of_err(res.unwrap_err())

    def or_else(self, op: Callable[[KE], Result[KT, F]]) -> Result[KT, F]:
        return op(self.__value)


from .option import Option
