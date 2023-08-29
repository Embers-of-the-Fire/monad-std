# Change Log

## V0.1.1

**ADD**

- [`monad_std.Option`](Api Document/option.md):
    - `__add__/+ __mul__/*`: Call on the contained value.
    - `__iter__/to_iter`: Adapt from `to_array` method.
- [`monad_std.Result`](Api Document/result.md):
    - `__add__/+ __mul__/*`: Call on the contained value.
    - `__iter__/to_iter`: Adapt from `to_array` method.

**FIX**

- [`monad_std.Option`](Api Document/option.md):
  Split into [`OpSome`](Api Document/Option-Impl.md#monad_std.option.OpSome)
  and [`OpNone`](Api Document/Option-Impl.md#monad_std.option.OpNone).

## V0.1.0

**ADD**

- `monad_std.std_types`: Wrapped api around std types.
    - [`MList`](Api Document/STD Types/pylist.md):
        - Rewrite `list.index`, `list.pop`: Now they'll return an `Option[T]`.
        - Add `MList.get`: Get an `Option` of the indexed value.
    - [`MTuple`](Api Document/STD Types/pytuple.md):
        - Rewrite `tuple.index`: Now it'll return an `Option`.
        - Add `MTuple.get`: Get an `Option` of the indexed value.
    - [`MSet`](Api Document/STD Types/pyset.md):
        - Rewrite `set.pop`: Now it'll return an `Option`.
    - [`MDict`](Api Document/STD Types/pydict.md):
        - Rewrite `dict.popitem`, `dict.pop`: Now they'll return an `Option`.
        - Add `MDict.get`: Get an `Option` of the keyed value.
- [`monad_std.Option`](Api Document/option.md):
    - Add [`from_nullable`](Api Document/option.md#monad_std.option.Option.from_nullable) as constructor.
    - Add `__bool__` magic method.
- [`monad_std.Result`](Api Document/result.md):
    - Add [`catch`](Api Document/result.md#monad_std.result.Result.catch)
      and [`catch_from`](Api Document/result.md#monad_std.result.Result.catch_from) as constructor.
    - Add `__bool__` magic method.

**FIX**

- [`monad_std.Option`](Api Document/option.md): Fix `Option.__repr__`'s behavior.

## V0.0.0(Initial Release)

**ADD**

- [`monad_std.Option`](Api Document/option.md): An optional value.
- [`monad_std.Result`](Api Document/result.md): A structure containing a success value or an error.
- [`monad_std.UnwrapException`](Api Document/error.md): Generic exception for unwrapping a monad.
