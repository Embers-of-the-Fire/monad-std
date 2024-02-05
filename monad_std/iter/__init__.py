import typing as t

from .iter import IterMeta, OnceWith, Repeat
from . import impl

__all__ = [
    "IterMeta",
    "impl",
    "siter",
    "once",
    "once_with",
    "repeat",
]

T = t.TypeVar("T")
T_co = t.TypeVar("T_co", covariant=True)


def siter(it: t.Union[t.Iterable[T_co], t.Iterator[T_co]]) -> IterMeta[T_co]:
    """See [`IterMeta.iter`][monad_std.iter.iter.IterMeta.iter] for more information."""
    return IterMeta.iter(it)


def once(value: T) -> IterMeta[T]:
    """See [`IterMeta.once`][monad_std.iter.iter.IterMeta.once] for more information."""
    return IterMeta.once(value)


def once_with(value: t.Callable[[], T_co]) -> OnceWith[T_co]:
    """See [`IterMeta.once_with`][monad_std.iter.iter.IterMeta.once_with] for more information."""
    return IterMeta.once_with(value)


def repeat(value: T) -> Repeat[T]:
    """See [`IterMeta.repeat`][monad_std.iter.iter.IterMeta.repeat] for more information."""
    return IterMeta.repeat(value)
