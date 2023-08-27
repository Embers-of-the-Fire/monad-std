from typing import TypeVar, List, SupportsIndex, Generic

from ..option import Option

KT = TypeVar('KT')


class MList(Generic[KT], List[KT]):
    def index(self, *args, **kwargs) -> Option[int]:
        try:
            return Option.of_some(super().index(*args, **kwargs))
        except ValueError:
            return Option.of_none()

    def get(self, index: SupportsIndex) -> Option[KT]:
        try:
            return Option.of_some(self.__getitem__(index))
        except IndexError:
            return Option.of_none()

    def pop(self, *args, **kwargs) -> Option[KT]:
        try:
            return Option.of_some(super().pop(*args, **kwargs))
        except (IndexError, AssertionError):
            return Option.of_none()
