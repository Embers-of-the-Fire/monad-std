import warnings
import typing as t

from monad_std.option import Option
from monad_std.result import Result
from ..iter import IterMeta

T = t.TypeVar("T")


class OnceWith(IterMeta[T], t.Generic[T]):
    __func: Option[t.Callable[[], T]]

    def __init__(self, func: t.Callable[[], T]):
        self.__func = Option.some(func)

    def next(self) -> Option[T]:
        if self.__func.is_some():
            val = self.__func.map(lambda s: s())
            self.__func = Option.none()
            return val
        else:
            return Option.none()

    def nth(self, n: int = 1) -> Option[T]:
        if self.__func.is_none():
            pass
        elif n > 0:
            self.__func = Option.none()
        else:
            val = self.__func.map(lambda s: s())
            self.__func = Option.none()
            return val

        return Option.none()

    def next_chunk(self, n: int = 2) -> Result[t.List[T], t.List[T]]:
        assert n > 0, "Chunk size must be positive"
        if n > 1:
            vale = list(self.__func.map(lambda s: s()).to_iter())
            self.__func = Option.none()
            return Result.of_err(vale)
        else:
            valo: Result[t.List[T], t.List[T]] = self.__func.map(lambda s: [s()]).ok_or([])
            self.__func = Option.none()
            return valo

    def advance_by(self, n: int = 0) -> Result[None, int]:
        if n == 0:
            return Result.of_ok(None)
        elif self.__func.is_none() and n > 0:
            return Result.of_err(n)
        else:
            self.__func = Option.none()
            if n == 1:
                return Result.of_ok(None)
            return Result.of_err(n - 1)

    def fuse(self) -> "OnceWith[T]":  # type: ignore[override]
        warnings.warn("Fusing repeated iterator is meaningless.", Warning)
        return self

    def skip(self, n: int) -> "OnceWith[T]":  # type: ignore[override]
        warnings.warn("Skip repeated iterator is meaningless.", Warning)
        return self
