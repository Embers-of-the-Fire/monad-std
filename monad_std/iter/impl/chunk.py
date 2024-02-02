import typing as t
import collections.abc

from ..iter import IterMeta
from monad_std import Option

from .array_chunk import ArrayChunk

T = t.TypeVar('T')
U = t.TypeVar('U')


class Chunk(IterMeta[t.List[T]], t.Generic[T]):
    __it: ArrayChunk[T]
    __finished: bool

    def __init__(self, it: IterMeta[T], chunk_size: int):
        assert chunk_size > 0, "Chunk size must be greater than zero!"
        self.__it = it.array_chunk(chunk_size)
        self.__finished = False

    def next(self) -> Option[t.List[T]]:
        if not self.__finished:
            nxt = self.__it.next()
            if nxt.is_none():
                unused = self.__it.get_unused()
                self.__finished = True
                return unused
            return nxt
        else:
            return Option.none()
