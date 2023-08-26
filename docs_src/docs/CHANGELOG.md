# Change Log

## V0.1.0

**ADD**

- `monad_std.std_types`: Wrapped api around std types.
    - [`MList`](/Api Document/STD Types/pylist):
        - Rewrite `list.index`, `list.pop`: Now they'll return an `Option[T]`.
        - Add `MList.get`: Get an `Option` of the indexed value.
    - [`MTuple`](/Api Document/STD Types/pytuple):
        - Rewrite `tuple.index`: Now it'll return an `Option`.
        - Add `MTuple.get`: Get an `Option` of the indexed value.
    - [`MSet`](/Api Document/STD Types/pyset):
        - Rewrite `set.pop`: Now it'll return an `Option`.
    - [`MDict`](/Api Document/STD Types/pydict):
        - Rewrite `dict.popitem`, `dict.pop`: Now they'll return an `Option`.
        - Add `MDict.get`: Get an `Option` of the keyed value.

**FIX**

- [`monad_std.Option`](/Api Document/option): Fix `Option.__repr__`'s behavior.

## V0.0.0(Initial Release)

**ADD**

- [`monad_std.Option`](/Api Document/option): An optional value.
- [`monad_std.Result`](/Api Document/result): A structure containing a success value or an error.
- [`monad_std.UnwrapException`](/Api Document/error): Generic exception for unwrapping a monad.
