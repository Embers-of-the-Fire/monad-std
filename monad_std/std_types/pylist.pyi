from typing import SupportsIndex, TypeVar, List, Generic

from ..option import Option

KT = TypeVar('KT')

class MList(Generic[KT], List[KT]):
    def index(self, __value: KT, __start: SupportsIndex = ..., __stop: SupportsIndex = ...) -> Option[int]:
        """Return first index of value.

        **Actual Method Signature**
        ```python
        def index(self, __value: KT,
            __start: SupportsIndex = ...,
            __stop: SupportsIndex = ...) -> Option[int]: ...
        ```

        Args:
            __value: Value to search for.
            __start: Start index.
            __stop: Stop index.

        Returns:
            First index of the value, or `Option::None` if there's no such item.

        Examples:
            ```python
            x = MList([1, 2, 3, 4, 5])
            assert x.index(2) == Option.of_some(1)
            assert x.index(0) == Option.of_none()
            ```
        """
    def get(self, index: SupportsIndex) -> Option[KT]:
        """Get an item from the list.

        Returns:
            The value at the given index, or `Option::None` if it's out of range.

        Examples:
            ```python
            x = MList([1, 2, 3, 4, 5])
            assert x.get(2) == Option.of_some(3)
            assert x.get(10) == Option.of_none()
            ```
        """
    def pop(self, __index: SupportsIndex = ...) -> Option[KT]:
        """Pop a value from the list.

        **Actual Method Signature**
        ```python
        def pop(self, __index: SupportsIndex = ...) -> Option[KT]: ...
        ```

        Args:
            __index: The index to pop. **Optional**

        Returns:
            The last value or the value at the given index, or `None` if it's out of range.

        Examples:
            ```python
            x = MList([1, 2, 3, 4, 5])
            assert x.pop() == Option.of_some(5)
            assert x.pop(1) == Option.of_some(2)
            x = MList()
            assert x.pop() == Option.of_none()
            ```
        """
