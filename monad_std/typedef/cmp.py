import typing as t
import typing_extensions as te

_T_contra = t.TypeVar("_T_contra", contravariant=True)


class SupportsDunderLT(t.Protocol[_T_contra]):
    def __lt__(self, __other: _T_contra) -> bool: ...


class SupportsDunderGT(t.Protocol[_T_contra]):
    def __gt__(self, __other: _T_contra) -> bool: ...


class SupportsDunderLE(t.Protocol[_T_contra]):
    def __le__(self, __other: _T_contra) -> bool: ...


class SupportsDunderGE(t.Protocol[_T_contra]):
    def __ge__(self, __other: _T_contra) -> bool: ...


class SupportsAllComparisons(
    SupportsDunderLT[_T_contra],
    SupportsDunderGT[_T_contra],
    SupportsDunderLE[_T_contra],
    SupportsDunderGE[_T_contra],
    t.Protocol[_T_contra]
):
    ...


class SupportsRichComparison(
    SupportsDunderLT[_T_contra],
    SupportsDunderGT[_T_contra],
    t.Protocol[_T_contra]
):
    ...


SupportsRichComparisonSelf: te.TypeAlias = SupportsRichComparison["SupportsRichComparisonSelf"]
SupportsRichComparisonSelfT = t.TypeVar("SupportsRichComparisonSelfT", bound=SupportsRichComparisonSelf)


class SupportsDunderEq(t.Protocol[_T_contra]):
    # This is just a protocol, so we don't need to satisfy the upper bound of `__eq__`.
    def __eq__(self, other: _T_contra) -> bool: ...  # type: ignore[override]


SupportsDunderEqSelf: te.TypeAlias = SupportsDunderEq["SupportsDunderEqSelf"]


class SupportsDunderHash(t.Protocol[_T_contra]):
    def __hash__(self) -> int: ...
