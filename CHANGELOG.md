# Change Log

## V0.9.0

**ADD**:

- `monad_std.iter.IterMeta`:
    - `map_while`: Yields elements based on both a predicate and maps.
    - `map_windows`: A map but with fixed-sized windows.
    - `max`, `min`: Get the maximum / minimum value.
    - `collect_to_xxx`: Collect the iterator into a mutable and extendable item.<br />
      Note that in Python it's not possible to actually *change* a `str`, so `collect_to_string` is not provided.
    - `collect_set`: Collect the iterator into a hashset.

**Impl Change**

- Use `import typing` instead of `from typing import ...` to make the scope and namespace cleaner.
- All iterator implementation will be moved to their single files,
  and can stil be imported from `monad_std.iter.impl`.

## V0.8.0

**ADD**:

- `monad_std.prelude`: module that contains all frequently used utilities.
- `monad_std.iter`:
    - `siter`: See `IterMeta.iter`.
    - `once`: See `IterMeta.once`.
    - `once_with`: See `IterMeta.once_with`.
    - `repeat`: See `IterMeta.repeat`.

## V0.7.0

**ADD**:

- `monad_std.Option`:
    - `map_mut`: Map a value by changing itself.
- `monad_std.Result`:
    - `map_mut`, `map_err_mut`: Map a value by changing itself.

**Breaking Change**

- Renamed all iterator tools' implement definition. Now they're not prefix-ed by an `_Iter`.
  You can now import them via `monad_std.iter.impl`.

## V0.6.0

**ADD**:

- `monad_std.iter.IterMeta`:
    - `chunk`: Data chunks which will return all the data, including those ignored ones by `array_chunk`.

## V0.5.0

**ADD**:

- `monad_std.Option`:
    - `to_pattern`: An alias for `unwrap_unchecked`.
- `monad_std.Result`:
    - `to_pattern`: Transfer into a tuple for pattern matching.
    - `ERR`, `OK`: Constant flag value. See `monad_std.Result.to_pattern`.

## V0.4.0

**ADD**

- `monad_std.Option`:
    - `to_nullable`/`unwrap_unchecked`: Convert `Option[T]` to `Optional[T]`.
- `monad_std.Result`:
    - `unwrap_unchecked`: Convert `Result[T, E]` to `Union[T, E]`.

## V0.3.0

**Breaking Change**

- `monad_std.Option`, `monad_std.Result`:
    - Move `transpose`, `flatten`, `unzip` from `staticmethod` to object method.

**Impl Change**

- `monad_std.Option`:
    - `__and__`, `__or__`, `__xor__` are not abstract methods now, and is implemented by `Option` itself.

**DOCUMENTATION**

- Move **STD Types** to one page.
- Add overview for API documentation.
- Add a quick start guide.

## V0.2.0

**ADD**

- `monad_std.iter.IterMeta`: Iterator tools.
    - Api List:
        - Iter builder:
            - `iter`
            - `once`
        - Iter pusher:
            - `advance_by`
            - `last`
            - `next_chunk`
            - `nth`
        - Iter sub tool: 
            - `enumerate`
            - `filter`, `filter_map`
            - `flat_map`, `flatten`
            - `fuse`
            - `inspect`
            - `intersperse`, `intersperse_with`
            - `map`
            - `peekable`
            - `scan`
            - `skip`
            - `take`, `take_while`
            - `zip`
        - Iter checker:
            - `all`, `any`
            - `exist`
        - Iter collector:
            - `count`
            - `fold`
            - `for_each`
            - `find`, `find_map`, `position`
            - `product`, `sum`
            - `reduce`
- `monad_std.Result`:
    - Exposed `Ok` and `Err` constructor.

**Breaking Change**

- `monad_std.Option`:
    - `of_some` -> `some`
    - `of_none` -> `none`

## V0.1.1

**ADD**

- `monad_std.Option`:
    - `__add__/+ __mul__/*`: Call on the contained value.
    - `__iter__/to_iter`: Adapt from `to_array` method.
- `monad_std.Result`:
    - `__add__/+ __mul__/*`: Call on the contained value.
    - `__iter__/to_iter`: Adapt from `to_array` method.

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
