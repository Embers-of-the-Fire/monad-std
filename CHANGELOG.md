# Change Log

## V0.2.0

**ADD**

- `monad_std.Option`:
    - `+/__add__`: These will now call on the contained value.
- `monad_std.Result`:
    - `+/__add__`: These will now call on the contained value.

**FIX**

- `monad_std.Option`: Split into `OpSome` and `OpNone`.

## V0.1.0

**ADD**

- `monad_std.std_types`: Wrapped api around std types.
    - `MList`:
        - Rewrite `list.index`, `list.pop`: Now they'll return an `Option[T]`.
        - Add `MList.get`: Get an `Option` of the indexed value.
    - `MTuple`:
        - Rewrite `tuple.index`: Now it'll return an `Option`.
        - Add `MTuple.get`: Get an `Option` of the indexed value.
    - `MSet`:
        - Rewrite `set.pop`: Now it'll return an `Option`.
    - `MDict`:
        - Rewrite `dict.popitem`, `dict.pop`: Now they'll return an `Option`.
        - Add `MDict.get`: Get an `Option` of the keyed value.
- `monad_std.Option`:
  - Add `from_nullable` as constructor.
  - Add `__bool__` magic method.
- `monad_std.Result`:
  - Add `catch` and `catch_from` as constructor.
  - Add `__bool__` magic method.

**FIX**

- `monad_std.Option`: Fix `Option.__repr__`'s behavior.

## V0.0.0(Initial Release)

**ADD**

- `monad_std.Option`: An optional value.
- `monad_std.Result`: A structure containing a success value or an error.
- `monad_std.UnwrapException`: Generic exception for unwrapping a monad.
