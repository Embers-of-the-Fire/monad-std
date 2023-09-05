from typing import Tuple, Any

from ..option import Option


class MTuple(Tuple):
    def index(self, *args, **kwargs) -> Option[int]:
        try:
            return Option.some(super().index(*args, **kwargs))
        except ValueError:
            return Option.none()

    def get(self, index: int) -> Option[Any]:
        try:
            return Option.some(self.__getitem__(index))
        except IndexError:
            return Option.none()

