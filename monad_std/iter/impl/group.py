import typing as t
import sys

from ..iter import IterMeta
from monad_std import typedef as td
from monad_std import Option
from .fuse import Fuse
from .peekable import Peekable

T = t.TypeVar("T")
K = t.TypeVar("K", covariant=True, bound=td.cmp.SupportsDunderEqSelf)


class Group(IterMeta[T], t.Generic[T, K]):
    __buffer: Option[IterMeta[T]]
    __parent: "GroupBy[T, K]"
    __end: bool

    def __init__(self, __parent: "GroupBy[T, K]"):
        self.__parent = __parent
        self.__buffer = Option.none()
        self.__end = False

    def _extend(self, el: t.List[T]):
        self.__buffer = Option.some(IterMeta.iter(el))

    def next(self) -> Option[T]:
        if self.__end:
            return Option.none()

        if self.__buffer.is_some():
            return self.__buffer.unwrap_unchecked().next()
        else:
            # noinspection PyProtectedMember
            nxt = self.__parent._sub_next()
            if nxt.is_some():
                return nxt
            else:
                self.__end = True
                return Option.none()


class GroupBy(IterMeta[t.Tuple[K, Group[T, K]]], t.Generic[T, K]):
    __it: Peekable[T, Fuse[T]]
    __current_yielding: Option[Group[T, K]]
    __current_yielding_key: Option[K]
    __predicate: t.Callable[[T], K]

    def __init__(self, __it: IterMeta[T], __predicate: t.Callable[[T], K]):
        self.__it = __it.fuse().peekable()
        self.__current_yielding = Option.none()
        self.__current_yielding_key = Option.none()
        self.__predicate = __predicate

    def _sub_next(self) -> Option[T]:
        if self.__it.peek().is_none():
            return Option.none()
        else:
            nxt = self.__it.peek().unwrap_unchecked()
            key = self.__predicate(nxt)
            if key == self.__current_yielding_key.unwrap_unchecked():
                return self.__it.next()
            else:
                return Option.none()

    def next(self) -> Option[t.Tuple[K, Group[T, K]]]:
        if self.__it.peek().is_none():
            del self.__current_yielding, self.__current_yielding_key
            return Option.none()
        elif self.__current_yielding.is_none() or self.__current_yielding_key.is_none():
            pass
        else:
            if sys.getrefcount(self.__current_yielding.unwrap_unchecked()) == 2:
                while (peek_nxt := self.__it.peek()).is_some():
                    nxt = peek_nxt.unwrap_unchecked()
                    key = self.__predicate(nxt)
                    if key != self.__current_yielding_key.unwrap_unchecked():
                        break
                    else:
                        self.__it.next()
            else:
                cls: t.List[T] = []

                while (peek_nxt := self.__it.peek()).is_some():
                    nxt = peek_nxt.unwrap_unchecked()
                    key = self.__predicate(nxt)
                    if key == self.__current_yielding_key.unwrap_unchecked():
                        cls.append(self.__it.next().unwrap_unchecked())
                    else:
                        break

                # noinspection PyProtectedMember
                self.__current_yielding.unwrap_unchecked()._extend(cls)

            self.__current_yielding = Option.none()
            self.__current_yielding_key = Option.none()

        peek_nxt = self.__it.peek()
        if peek_nxt.is_none():
            del self.__it  # the inner iterator is fused and can be safely deleted.
            return Option.none()
        key = self.__predicate(peek_nxt.unwrap_unchecked())
        self.__current_yielding_key = Option.some(key)
        group = Group(self)
        self.__current_yielding = Option.some(group)
        return Option.some((key, group))

