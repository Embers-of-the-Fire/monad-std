import warnings
import typing as t
import copy

from monad_std.option import Option
from monad_std.result import Result, Err, Ok
from ..iter import IterMeta

T = t.TypeVar("T")
U = t.TypeVar("U")


class Repeat(IterMeta[T], t.Generic[T]):
    __val: T

    def __init__(self, value: T):
        self.__val = value

    def next(self) -> Option[T]:
        return Option.some(copy.deepcopy(self.__val))

    def nth(self, n: int = 1) -> Option[T]:
        return Option.some(copy.deepcopy(self.__val))

    def advance_by(self, n: int = 0) -> Result[None, int]:
        return Ok(None)

    def next_chunk(self, n: int = 2) -> Result[t.List[T], t.List[T]]:
        assert n > 0, "Chunk size must be positive"
        return Ok([copy.deepcopy(self.__val) for _ in range(n)])

    def any(self, func: t.Callable[[T], bool] = lambda x: bool(x)) -> bool:
        return func(self.__val)

    def all(self, func: t.Callable[[T], bool] = lambda x: bool(x)) -> bool:
        return func(self.__val)

    def count(self) -> int:
        raise ValueError("Repeat iterator is infinitive and you cannot count it.")

    def find(self, predicate: t.Callable[[T], bool]) -> Option[T]:
        if predicate(self.__val):
            return Option.some(copy.deepcopy(self.__val))
        else:
            return Option.none()

    def find_map(self, func: t.Callable[[T], Option[U]]) -> Option[U]:
        return func(self.__val)

    def fuse(self) -> "Repeat[T]":  # type: ignore[override]
        warnings.warn("Fusing repeated iterator is meaningless.", Warning)
        return self

    def skip(self, n: int) -> "Repeat[T]":  # type: ignore[override]
        warnings.warn("Skip repeated iterator is meaningless.", Warning)
        return self
