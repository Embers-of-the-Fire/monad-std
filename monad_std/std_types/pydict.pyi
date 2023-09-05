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
            assert x.get('b') == Option.some(2)
            assert x.get('d') == Option.none()
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
            assert x.popitem() == Option.some(('a', 1))
            assert x.popitem() == Option.none()
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
            assert x.pop('a') == Option.some(1)
            assert x.pop('b') == Option.none()
            assert x.pop('a') == Option.none()
            ```
        """