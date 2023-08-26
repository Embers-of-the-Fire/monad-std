from typing import Tuple, Any

from ..option import Option


class MTuple(Tuple):
    def index(self, *args, **kwargs) -> Option[int]:
        try:
            return Option.of_some(super().index(*args, **kwargs))
        except ValueError:
            return Option.of_none()

    def get(self, index: int) -> Option[Any]:
        try:
            return Option.of_some(self.__getitem__(index))
        except IndexError:
            return Option.of_none()

