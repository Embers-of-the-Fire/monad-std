from typing import TypeVar, Generic, Dict

from .pytuple import MTuple
from ..option import Option

K = TypeVar('K')
V = TypeVar('V')


class MDict(Generic[K, V], Dict[K, V]):
    def get(self, key: K) -> Option[V]:
        """Get the value by the key.

        Args:
            key: The key to the value you want.

        Examples:
            ```python
            x = MDict({'a': 1, 'b': 2, 'c': 3})
            assert x.get('b') == Option.of_some(2)
            assert x.get('d') == Option.of_none()
            ```
        """
    def popitem(self) -> Option[MTuple[K, V]]:
        """Remove and return a (key, value) pair as a 2-tuple.

        Pairs are returned in LIFO (last-in, first-out) order.

        Returns:
            An optional key-value pair.

        Examples:
            ```python
            x = MDict({'a': 1})
            assert x.popitem() == Option.of_some(('a', 1))
            assert x.popitem() == Option.of_none()
            ```
        """
    def pop(self, key: K) -> Option[V]:
        """Pop a value from the dict.

        Args:
            key: The key to pop.

        Returns:
            The value under the key

        Examples:
            ```python
            x = MDict({'a': 1})
            assert x.pop('a') == Option.of_some(1)
            assert x.pop('b') == Option.of_none()
            assert x.pop('a') == Option.of_none()
            ```
        """