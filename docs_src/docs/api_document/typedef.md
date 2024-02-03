# Internal Type Definitions

Since std libraries are not implemented in python, only `pyi` files are provided to use.

However, this library is implemented with pure Python, and there's no need to write single
type definitions, which means we cannot use the `typeshed` package.

For internal use and for static type checking, part of the `typeshed` package is copied
and partly changed. It is guaranteed that the `monad-std` package will not use any of the
code except for type hints.

## `typedef.cmp`

Comparation-related types and protocols.

::: monad_std.typedef.cmp.SupportsDunderLT
    options:
        heading_level: 3

::: monad_std.typedef.cmp.SupportsDunderGT
    options:
        heading_level: 3

::: monad_std.typedef.cmp.SupportsDunderLE
    options:
        heading_level: 3

::: monad_std.typedef.cmp.SupportsDunderGE
    options:
        heading_level: 3

::: monad_std.typedef.cmp.SupportsAllComparisons
    options:
        heading_level: 3

::: monad_std.typedef.cmp.SupportsRichComparison
    options:
        heading_level: 3

## `typedef.ops`

Operation-related types and protocols.

::: monad_std.typedef.ops.SupportsAdd
    options:
        heading_level: 3

::: monad_std.typedef.ops.SupportsRAdd
    options:
        heading_level: 3

::: monad_std.typedef.ops.SupportsSub
    options:
        heading_level: 3

::: monad_std.typedef.ops.SupportsRSub
    options:
        heading_level: 3

::: monad_std.typedef.ops.SupportsMul
    options:
        heading_level: 3

::: monad_std.typedef.ops.SupportsRMul
    options:
        heading_level: 3

::: monad_std.typedef.ops.SupportsDivMod
    options:
        heading_level: 3

::: monad_std.typedef.ops.SupportsRDivMod
    options:
        heading_level: 3
