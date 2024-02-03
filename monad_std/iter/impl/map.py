import typing as t
import typing_extensions as te
import collections
import warnings

from ..iter import IterMeta
from monad_std import Option

T = t.TypeVar('T')
U = t.TypeVar('U')
R = t.TypeVar('R')


class Map(IterMeta[U], t.Generic[T, U]):
    __it: IterMeta[T]
    __func: t.Callable[[T], U]

    def __init__(self, __it: IterMeta[T], __func: t.Callable[[T], U]):
        self.__it = __it
        self.__func = __func

    def next(self) -> Option[U]:
        return self.__it.next().map(self.__func)


class MapWhile(IterMeta[U], t.Generic[T, U]):
    __it: IterMeta[T]
    __func: t.Callable[[T], Option[U]]

    def __init__(self, __it: IterMeta[T], __func: t.Callable[[T], Option[U]]):
        self.__it = __it
        self.__func = __func

    def next(self) -> Option[U]:
        return self.__it.next().and_then(lambda v: self.__func(v))


class MapWindows(IterMeta[R], t.Generic[T, R]):
    __const_len: int
    __it: Option[IterMeta[T]]
    __buffer: Option[t.Deque[T]]
    __func: t.Callable[[t.Deque[T]], R]

    def __init__(self, __const_len: int, __it: IterMeta[T], __func: t.Callable[[t.Deque[T]], R]):
        assert __const_len >= 1, "window size must be larger than 1"
        self.__const_len = __const_len
        self.__it = Option.some(__it)
        self.__func = __func
        self.__buffer = Option.some(collections.deque(maxlen=__const_len))

    def __push_window(self):
        if self.__buffer.is_some() and self.__it.is_some():
            buf = self.__buffer.unwrap_unchecked()
            if len(buf) < self.__const_len:
                while len(buf) < self.__const_len\
                        and (x := self.__it.unwrap_unchecked().next()).is_some():
                    buf.append(x.unwrap_unchecked())
                if len(buf) < self.__const_len:
                    self.__buffer = Option.none()
                    self.__it = Option.none()
            else:
                if (x := self.__it.unwrap_unchecked().next()).is_some():
                    x = x.unwrap_unchecked()
                    buf.popleft()
                    buf.append(x)
                else:
                    self.__buffer = Option.none()
                    self.__it = Option.none()

    def next(self) -> Option[R]:
        self.__push_window()
        return self.__buffer.map(lambda buf: self.__func(buf))

    @te.override
    def fuse(self) -> "MapWindows[T, R]": # type: ignore[override]
        warnings.warn("MapWindows is already fused.", Warning)
        return self
