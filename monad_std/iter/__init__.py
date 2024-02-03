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


V = t.TypeVar("V")


def siter(it: t.Union[t.Iterable[V], t.Iterator[V]]) -> IterMeta[V]:
    """See [`IterMeta.iter`][monad_std.iter.iter.IterMeta.iter] for more information."""
    return IterMeta.iter(it)


def once(value: V) -> IterMeta[V]:
    """See [`IterMeta.once`][monad_std.iter.iter.IterMeta.once] for more information."""
    return IterMeta.once(value)

def once_with(value: t.Callable[[], V]) -> OnceWith[V]:
    """See [`IterMeta.once_with`][monad_std.iter.iter.IterMeta.once_with] for more information."""
    return IterMeta.once_with(value)


def repeat(value: V) -> Repeat[V]:
    """See [`IterMeta.repeat`][monad_std.iter.iter.IterMeta.repeat] for more information."""
    return IterMeta.repeat(value)

