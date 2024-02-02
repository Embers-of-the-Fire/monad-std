import typing as t

from ..option import Option

KT = t.TypeVar('KT')


class MList(t.Generic[KT], t.List[KT]):
    def index(self, *args, **kwargs) -> Option[int]:
        try:
            return Option.some(super().index(*args, **kwargs))
        except ValueError:
            return Option.none()

    def get(self, index: t.SupportsIndex) -> Option[KT]:
        try:
            return Option.some(self.__getitem__(index))
        except IndexError:
            return Option.none()

    def pop(self, *args, **kwargs) -> Option[KT]:
        try:
            return Option.some(super().pop(*args, **kwargs))
        except (IndexError, AssertionError):
            return Option.none()
