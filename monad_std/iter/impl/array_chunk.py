import typing as t

from ..iter import IterMeta
from monad_std import Option

T = t.TypeVar('T')
U = t.TypeVar('U')


class ArrayChunk(IterMeta[t.List[T]], t.Generic[T]):
    __it: IterMeta[T]
    __chunk_size: int
    __unused: Option[t.List[T]]

    def __init__(self, it: IterMeta[T], chunk_size: int):
        assert chunk_size > 0, "Chunk size must be greater than zero!"
        self.__it = it
        self.__chunk_size = chunk_size

    def next(self) -> Option[t.List[T]]:
        arr = []
        for _ in range(self.__chunk_size):
            if (x := self.__it.next()).is_some():
                arr.append(x.unwrap())
            else:
                break
        else:
            # short-circuit here if we don't meet any Option::None
            return Option.some(arr)
        self.__unused = Option.some(arr)
        return Option.none()

    def get_unused(self) -> Option[t.List[T]]:
        """Return the last/unused several elements.

        Examples:
            ```python
            it = IterMeta.iter([1, 2, 3, 4]).array_chunk(3)
            assert it.next() == Option.some([1, 2, 3])
            assert it.next() == Option.none()
            assert it.get_unused() == Option.some([4])
            ```
        """
        return self.__unused
