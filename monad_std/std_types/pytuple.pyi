from typing import Tuple, SupportsIndex, Any

from ..option import Option


class MTuple(Tuple):
    def index(
            self,
            __value: Any,
            __start: SupportsIndex = ...,
            __stop: SupportsIndex = ...
        ) -> int: # type: ignore[override]
        """Return first index of value.

        **Actual Method Signature**
        ```python
        def index(self, __value: Any,
            __start: SupportsIndex = ...,
            __stop: SupportsIndex = ...) -> Option[int]: ...
        ```

        Args:
            __value: Value to search for.
            __start: Start index.
            __stop: Stop index.

        Returns:
            First index of the value, or `Option::None` if there's no such item.
        """

    def get(self, index: int) -> Option[Any]: # type: ignore[override]
        """Get an item from the tuple.

        Returns:
            The value at the given index, or `Option::None` if it's out of range.
        """
