import typing as t
import collections

from ..iter import IterMeta
from monad_std import Either, Option

T = t.TypeVar("T")
L = t.TypeVar("L")
R = t.TypeVar("R")
B = t.TypeVar("B")


class PartitionBy(t.Generic[T, L, R]):
    __spliter: t.Callable[[T], Either[L, R]]
    __it: IterMeta[T]
    __end: bool

    __child_1: "PartitionGroup[T, L, R, L]"
    __child_2: "PartitionGroup[T, L, R, R]"

    def __init__(self, __it: IterMeta[T], __spliter: t.Callable[[T], Either[L, R]]):
        self.__spliter = __spliter
        self.__it = __it
        self.__end = False

        self.__child_1 = PartitionGroup(self, lambda: self.__next_left())
        self.__child_2 = PartitionGroup(self, lambda: self.__next_right())

    @staticmethod
    def init(
            __it: IterMeta[T],
            __spliter: t.Callable[[T], Either[L, R]]
    ) -> "t.Tuple[PartitionBy[T, L, R], PartitionGroup[T, L, R, L], PartitionGroup[T, L, R, R]]":
        pb = PartitionBy(__it, __spliter)
        return pb, pb.__child_1, pb.__child_2

    def __next(self) -> Option[Either[L, R]]:
        if self.__end:
            return Option.none()
        nxt = self.__it.next()
        if nxt.is_none():
            self.__end = True
            del self.__it
            return Option.none()
        else:
            return nxt.map(lambda x: self.__spliter(x))

    def __next_left(self) -> Option[L]:
        while True:
            _nxt = self.__next()
            if _nxt.is_none():
                del self.__child_1
                return Option.none()
            nxt = _nxt.unwrap_unchecked()
            if nxt.is_left():
                return Option.some(nxt.unwrap_left_unchecked())
            else:
                # noinspection PyProtectedMember
                self.__child_2._push_buffer(nxt.unwrap_right_unchecked())

    def __next_right(self) -> Option[R]:
        while True:
            _nxt = self.__next()
            if _nxt.is_none():
                del self.__child_2
                return Option.none()
            nxt = _nxt.unwrap_unchecked()
            if nxt.is_right():
                return Option.some(nxt.unwrap_right_unchecked())
            else:
                # noinspection PyProtectedMember
                self.__child_1._push_buffer(nxt.unwrap_left_unchecked())


class PartitionGroup(IterMeta[B], t.Generic[T, L, R, B]):
    __parent: PartitionBy[T, L, R]
    __end: bool
    __buffer: t.Deque[B]
    __parent_next: t.Callable[[], Option[B]]

    def __init__(self, __parent: PartitionBy[T, L, R], __parent_next: t.Callable[[], Option[B]]):
        self.__parent = __parent
        self.__end = False
        self.__parent_next = __parent_next
        self.__buffer = collections.deque()

    def next(self) -> Option[B]:
        if self.__end and self.__buffer:
            return Option.none()
        if len(self.__buffer) == 0:
            nxt = self.__parent_next()
            if nxt.is_none():
                self.__end = True
                del self.__parent, self.__parent_next, self.__buffer
                return Option.none()
            return nxt
        else:
            return Option.some(self.__buffer.popleft())

    def _push_buffer(self, item: B):
        self.__buffer.append(item)
