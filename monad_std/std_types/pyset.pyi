from typing import TypeVar, Generic, Set

from ..option import Option

K = TypeVar('K')


class MSet(Generic[K], Set[K]):
    def pop(self) -> Option[K]:
        """Remove and return an arbitrary set element.

        Returns:
            The popped element.

        Examples:
            ```python
            x = MSet([1, 'd'])
            p1 = x.pop()
            assert p1 == Option.of_some(1) or p1 == Option.of_some('d')
            x.pop()
            assert x.pop() == Option.of_none()
            ```
        """
