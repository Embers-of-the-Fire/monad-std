# Change Log

## V0.7.0

**ADD**:

- [`monad_std.Option`][monad_std.option.Option]:
    - [`map_mut`][monad_std.option.Option.map_mut]: Map a value by changing itself.
- [`monad_std.Result`][monad_std.result.Result]:
    - [`map_mut`][monad_std.result.Result.map_mut], [`map_err_mut`][monad_std.result.Result.map_err_mut]:
      Map a value by changing itself.

**Breaking Change**

- Renamed all iterator tools' implement definition. Now they're not prefix-ed by an `_Iter`.
  You can now import them via `monad_std.iter.impl`.

## V0.6.0

**ADD**:

- [`monad_std.iter.IterMeta`][monad_std.iter.iter.IterMeta]:
    - [`chunk`][monad_std.iter.iter.IterMeta.chunk]: Data chunks which will return all the data,
      including those ignored ones by [`array_chunk`][monad_std.iter.iter.IterMeta.array_chunk].

## V0.5.0

**ADD**:

- [`monad_std.Option`][monad_std.option.Option]:
    - [`to_pattern`][monad_std.option.Option.to_pattern]:
        An alias for [`unwrap_unchecked`][monad_std.option.Option.unwrap_unchecked].
- [`monad_std.Result`][monad_std.result.Result]:
    - [`to_pattern`][monad_std.option.Result.to_pattern]: Transfer into a tuple for pattern matching.
    - [`ERR`][monad_std.option.Result.ERR], [`OK`][monad_std.option.Result.OK]: Constant flag value.
        See [`monad_std.Result.to_pattern`][monad_std.option.Result.to_pattern].

## V0.4.0

**ADD**

- [`monad_std.Option`][monad_std.option.Option]:
    - [`to_nullable`][monad_std.option.Option.to_nullable]
      /[`unwrap_unchecked`][monad_std.option.Option.unwrap_unchecked]: Convert `Option[T]` to `Optional[T]`.
- [`monad_std.Result`][monad_std.result.Result]:
    - [`unwrap_unchecked`][monad_std.result.Result.unwrap_unchecked]: Convert `Result[T, E]` to `Union[T, E]`.

## V0.3.0

**Breaking Change**

- [`monad_std.Option`][monad_std.option.Option], [`monad_std.Result`][monad_std.result.Result]:
    - Move `transpose`, `flatten`, `unzip` from `staticmethod` to object method.

**Impl Change**

- [`monad_std.Option`][monad_std.option.Option]:
    - [`__and__`][monad_std.option.Option.__and__], [`__or__`][monad_std.option.Option.__or__],
      [`__xor__`][monad_std.option.Option.__xor__] are not abstract methods now,
      and is implemented by [`Option`][monad_std.option.Option] itself.

**DOCUMENTATION**

- Move **STD Types** to one page.
- Add overview for API documentation.
- Add a quick start guide.

## V0.2.0

**ADD**

- [`monad_std.iter.IterMeta`][monad_std.iter.iter.IterMeta]: Iterator tools.
    - Api List:
        - Iter builder:
            - [`iter`][monad_std.iter.iter.IterMeta.iter]
            - [`once`][monad_std.iter.iter.IterMeta.once]
        - Iter pusher:
            - [`advance_by`][monad_std.iter.iter.IterMeta.advance_by]
            - [`last`][monad_std.iter.iter.IterMeta.last]
            - [`next_chunk`][monad_std.iter.iter.IterMeta.next_chunk]
            - [`nth`][monad_std.iter.iter.IterMeta.nth]
        - Iter sub tool: 
            - [`enumerate`][monad_std.iter.iter.IterMeta.enumerate]
            - [`filter`][monad_std.iter.iter.IterMeta.filter], [`filter_map`][monad_std.iter.iter.IterMeta.filter_map]
            - [`flat_map`][monad_std.iter.iter.IterMeta.flat_map], [`flatten`][monad_std.iter.iter.IterMeta.flatten]
            - [`fuse`][monad_std.iter.iter.IterMeta.fuse]
            - [`inspect`][monad_std.iter.iter.IterMeta.inspect]
            - [`intersperse`][monad_std.iter.iter.IterMeta.intersperse],
              [`intersperse_with`][monad_std.iter.iter.IterMeta.intersperse_with]
            - [`map`][monad_std.iter.iter.IterMeta.map]
            - [`peekable`][monad_std.iter.iter.IterMeta.peekable]
            - [`scan`][monad_std.iter.iter.IterMeta.scan]
            - [`skip`][monad_std.iter.iter.IterMeta.skip]
            - [`take`][monad_std.iter.iter.IterMeta.take], [`take_while`][monad_std.iter.iter.IterMeta.take_while]
            - [`zip`][monad_std.iter.iter.IterMeta.zip]
        - Iter checker:
            - [`all`][monad_std.iter.iter.IterMeta.all], [`any`][monad_std.iter.iter.IterMeta.any]
            - [`exist`][monad_std.iter.iter.IterMeta.exist]
        - Iter collector:
            - [`count`][monad_std.iter.iter.IterMeta.count]
            - [`fold`][monad_std.iter.iter.IterMeta.fold]
            - [`for_each`][monad_std.iter.iter.IterMeta.for_each]
            - [`find`][monad_std.iter.iter.IterMeta.find], [`find_map`][monad_std.iter.iter.IterMeta.find_map],
              [`position`][monad_std.iter.iter.IterMeta.position]
            - [`product`][monad_std.iter.iter.IterMeta.product], [`sum`][monad_std.iter.iter.IterMeta.sum]
            - [`reduce`][monad_std.iter.iter.IterMeta.reduce]
- [`monad_std.Result`](Api Document/result.md):
    - Exposed [`Ok`][monad_std.result.Ok] and [`Err`][monad_std.result.Err] constructor.

**Breaking Change**

- [`monad_std.Option`](Api Document/option.md):
    - `of_some` -> [`some`][monad_std.result.Option.some]
    - `of_none` -> [`none`][monad_std.result.Option.none]

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
    - [`MList`][monad_std.std_types.MList]:
        - Rewrite `list.index`, `list.pop`: Now they'll return an `Option[T]`.
        - Add `MList.get`: Get an `Option` of the indexed value.
    - [`MTuple`][monad_std.std_types.MTuple]:
        - Rewrite `tuple.index`: Now it'll return an `Option`.
        - Add `MTuple.get`: Get an `Option` of the indexed value.
    - [`MSet`][monad_std.std_types.MSet]:
        - Rewrite `set.pop`: Now it'll return an `Option`.
    - [`MDict`][monad_std.std_types.MDict]:
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
