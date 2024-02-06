import typing as t
from abc import ABCMeta, abstractmethod

from .error import UnwrapException

L = t.TypeVar("L")
R = t.TypeVar("R")
HL = t.TypeVar("HL", bound=t.Hashable)
HR = t.TypeVar("HR", bound=t.Hashable)

class Either(t.Generic[L, R], metaclass=ABCMeta):
    """An ancestor class of any `Either` type, inherited by `Left` and `Right`."""

    #################
    # Dunder method #
    #################

    @abstractmethod
    def __eq__(self, other: object) -> bool:
        ...

    @abstractmethod
    def __hash__(self: "Either[HL, HR]") -> int:
        ...

    @abstractmethod
    def __str__(self) -> str:
        ...

    @abstractmethod
    def __repr__(self) -> str:
        ...

    def __instancecheck__(self, instance) -> bool:
        return isinstance(instance, (Left, Right))

    #################
    # Static method #
    #################

    @staticmethod
    def of_left(value: L) -> "Left[L, R]":
        """Create a `Left` value."""
        return Left(value)
    
    @staticmethod
    def of_right(value: R) -> "Right[L, R]":
        """Create a `Right` value."""
        return Right(value)
    
    #################
    # Object method #
    #################

    # Type checking #

    @abstractmethod
    def is_left(self) -> bool:
        """Returns `True` if the value is a `Left`.
        
        Examples:
            ```python
            assert Left(5).is_left()
            assert not Right(5).is_left()
            ```
        """
        ...

    @abstractmethod
    def is_right(self) -> bool:
        """Returns `True` if the value is a `Right`.
        
        Examples:
            ```python
            assert not Left(5).is_right()
            assert Right(5).is_right()
            ```
        """
        ...

    # Unwrapping #

    @abstractmethod
    def unwrap_left(self) -> L:
        """Returns the contained `Left` value.
        
        This method may raise an exception.
        
        Raises:
            UnwrapException: Raises if the value is a `Right`.
        
        Examples:
            ```python
            assert Left(5).unwrap_left() == 5
            try:
                Right(5).unwrap_left()
            except UnwrapException as e:
                assert str(e) == "EitherError: Call `Either.unwrap_left` on a `Right` value."
            ```
        """
        ...

    @abstractmethod
    def unwrap_right(self) -> R:
        """Returns the contained `Right` value.
        
        This method may raise an exception.
        
        Raises:
            UnwrapException: Raises if the value is a `Left`.
        
        Examples:
            ```python
            assert Right(5).unwrap_right() == 5
            try:
                Left(5).unwrap_right()
            except UnwrapException as e:
                assert str(e) == "EitherError: Call `Either.unwrap_right` on a `Left` value."
            ```
        """
        ...
    
    @abstractmethod
    def unwrap_left_unchecked(self) -> L:
        """Returns the contained `Left` value.

        This method acually returns `Optional[L]` instead of `L`.
        But it hide the `None` in the type hint.

        The null safety should be guaranteed by the caller.
        """
        ...

    @abstractmethod
    def unwrap_right_unchecked(self) -> R:
        """Returns the contained `Right` value.

        This method acually returns `Optional[R]` instead of `R`.
        But it hide the `None` in the type hint.
        
        The null safety should be guaranteed by the caller.
        """
        ...


class Left(t.Generic[L, R], Either[L, R]):
    __value: L

    def __init__(self, value: L):
        self.__value = value
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, Left):
            return self.__value == other.__value
        elif isinstance(other, Right):
            return False
        else:
            raise TypeError("An `Either` can only be conpared with another `Either`")

    def __hash__(self: "Left[HL, HR]") -> int:
        return hash((True, self.__value))
    
    def __str__(self) -> str:
        return str(self.__value)
    
    def __repr__(self) -> str:
        return f"Either::Left({self.__value})"
    
    def __instancecheck__(self, instance) -> bool:
        return isinstance(instance, Left)
    
    def is_left(self) -> bool:
        return True
    
    def is_right(self) -> bool:
        return False
    
    def unwrap_left(self) -> L:
        return self.__value
    
    def unwrap_right(self) -> R:
        raise UnwrapException(
            "Either",
            "Call `Either.unwrap_right` on a `Left` value."
        )
    
    def unwrap_left_unchecked(self) -> L:
        return self.__value
    
    def unwrap_right_unchecked(self) -> R:
        # This is safe because the api asks the caller
        # to guarentee the call's safety.
        return None # type: ignore[return-value]


class Right(t.Generic[L, R], Either[L, R]):
    __value: R
    
    def __init__(self, value: R):
        self.__value = value
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, Right):
            return self.__value == other.__value
        elif isinstance(other, Left):
            return False
        else:
            raise TypeError("An `Either` can only be conpared with another `Either`")

    def __hash__(self: "Right[HL, HR]") -> int:
        return hash((False, self.__value))
    
    def __str__(self) -> str:
        return str(self.__value)
    
    def __repr__(self) -> str:
        return f"Either::Right({self.__value})"
    
    def __instancecheck__(self, instance) -> bool:
        return isinstance(instance, Right)
    
    def is_left(self) -> bool:
        return False
    
    def is_right(self) -> bool:
        return True
    
    def unwrap_left(self) -> L:
        raise UnwrapException(
            "Either",
            "Call `Either.unwrap_left` on a `Right` value."
        )
    
    def unwrap_right(self) -> R:
        return self.__value
    
    def unwrap_left_unchecked(self) -> L:
        # This is safe because the api asks the caller
        # to guarentee the call's safety.
        return None # type: ignore[return-value]
    
    def unwrap_right_unchecked(self) -> R:
        return self.__value
