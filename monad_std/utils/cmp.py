from enum import IntEnum, unique
import typing as t
import typing_extensions as te

from .. import typedef as td

DeprecatedOrdering: te.TypeAlias = t.Literal[0, -1, 1]
"""This type refers to that Python2 uses to represent ordering in, for example, the `sorted` function."""


@unique
class Ordering(IntEnum):
    """Basic ordering enum.

    This enum represents an ordering between two items.

    Python does not offer a standard way to represent ordering,
    and has different usages in different versions
    (e.g. Python2 uses positive/negative number).
    And this util class is used to standardize the ordering.

    Some of the api offered by this library will use this representation,
    and translations from other types is also available."""
    Greater = 0
    Equal = 1
    Less = 2

    def to_cmp(self) -> DeprecatedOrdering:
        """Transfer the ordering to the deprecated ordering representation.

        Returns:
            See [`DeprecatedOrdering`][monad_std.utils.cmp.DeprecatedOrdering] for more information.
        """
        if self == Ordering.Greater:
            return 1
        elif self == Ordering.Less:
            return -1
        else:
            return 0

    @staticmethod
    def parse(arg: t.Union[int, float, "Ordering"]) -> "Ordering":
        """Detect an ordering and returns an `Ordering`.

        Examples:
            ```python
            o1 = Ordering.parse(Ordering.Less)
            o2 = Ordering.parse(-1)
            o3 = Ordering.parse(-4.2)
            assert o1 == o2 == o3
            ```
        """
        if isinstance(arg, Ordering):
            return arg
        elif isinstance(arg, (int, float)):
            return Ordering.from_num(arg)
        else:
            raise ValueError("Unknown ordering type, expect `Ordering`, `int` or `float`")

    @staticmethod
    def from_cmp(cmp: DeprecatedOrdering) -> "Ordering":
        """Construct the ordering from the deprecated ordering representation.

        This has the same internal implementation as the [`from_num`][monad_std.utils.cmp.Ordering.from_num] method.
        However, this takes `DeprecatedOrdering` as argument instead of anything that can compare with `0`.
        The motivation of this specialized method is to guarantee type safety.

        It's also recommended to use this method to specify your target and what you want.
        But for more general use, you can also choose to use `from_num` instead.

        Args:
            cmp: See [`DeprecatedOrdering`][monad_std.utils.cmp.DeprecatedOrdering] for more information.

        Examples:
            ```python
            assert Ordering.from_cmp(0) == Ordering.Equal
            assert Ordering.from_cmp(1) == Ordering.Greater
            assert Ordering.from_cmp(-1) == Ordering.Less
            ```
        """
        if cmp > 0:
            return Ordering.Greater
        elif cmp < 0:
            return Ordering.Less
        else:
            return Ordering.Equal

    @staticmethod
    def from_num(n: "td.cmp.SupportsAllComparisons[int]") -> "Ordering":
        """Construct the ordering from the deprecated ordering representation.

        This accepts any value that can compare with `int` (or more explicitly `0`),
        different from [`from_cmp`][monad_std.utils.cmp.Ordering.from_cmp].

        It's generally discouraged to use this method.

        Examples:
            ```python
            assert Ordering.from_num(0.0) == Ordering.Equal
            assert Ordering.from_num(1.5) == Ordering.Greater
            assert Ordering.from_num(-3.2) == Ordering.Less
            ```
        """
        if n > 0:
            return Ordering.Greater
        elif n < 0:
            return Ordering.Less
        else:
            return Ordering.Equal

    def is_ne(self) -> bool:
        """If the ordering represents **not equal**."""
        return self != Ordering.Equal

    def is_le(self) -> bool:
        """If the ordering represents **less than or equal**."""
        return self != Ordering.Greater

    def is_ge(self) -> bool:
        """If the ordering represents **greater than or equal**."""
        return self != Ordering.Less
