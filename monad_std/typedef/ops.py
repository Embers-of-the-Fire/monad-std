import typing as t
import typing_extensions as te

if t.TYPE_CHECKING:
    _T = t.TypeVar("_T", covariant=True)


    class SupportsAdd(t.Protocol[_T]):
        def __add__(self, __x: te.Self) -> te.Self: ...


    class SupportsRAdd(t.Protocol[_T]):
        def __radd__(self, __x: te.Self) -> te.Self: ...


    class SupportsSub(t.Protocol[_T]):
        def __sub__(self, __x: te.Self) -> te.Self: ...


    class SupportsRSub(t.Protocol[_T]):
        def __rsub__(self, __x: te.Self) -> te.Self: ...


    class SupportsMul(t.Protocol[_T]):
        def __mul__(self, __x: te.Self) -> te.Self: ...
    

    class SupportsRMul(t.Protocol[_T]):
        def __rmul__(self, __x: te.Self) -> te.Self: ...


    class SupportsDivMod(t.Protocol[_T]):
        def __divmod__(self, __other: te.Self) -> te.Self: ...


    class SupportsRDivMod(t.Protocol[_T]):
        def __rdivmod__(self, __other: te.Self) -> te.Self: ...
