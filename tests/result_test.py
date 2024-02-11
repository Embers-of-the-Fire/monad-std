import unittest

from monad_std.prelude import *
from monad_std import UnwrapException


class ResultTest(unittest.TestCase):
    def test_identify(self):
        self.assertTrue(Result.of_ok(2).is_ok())
        self.assertFalse(Result.of_ok(2).is_err())
        self.assertFalse(Result.of_err("err").is_ok())
        self.assertTrue(Result.of_err("err").is_err())

        self.assertTrue(Result.of_ok(2).is_ok_and(lambda x: x > 1))
        self.assertFalse(Result.of_ok(0).is_ok_and(lambda x: x > 1))
        self.assertFalse(Result.of_err("error").is_ok_and(lambda x: x > 1))

        self.assertFalse(Result.of_ok(2).is_err_and(lambda x: len(x) == 3))
        self.assertTrue(Result.of_err("err").is_err_and(lambda x: len(x) == 3))
        self.assertFalse(Result.of_err("error").is_err_and(lambda x: len(x) == 3))
    
    def test_to_either(self):
        self.assertEqual(Ok(1).to_either(), Left(1))
        self.assertEqual(Err(1).to_either(), Right(1))

    def test_magic_method(self):
        self.assertTrue(Ok(2))
        self.assertFalse(Err("err"))

        self.assertEqual(Ok(2), Ok(1) + Ok(1))

        self.assertEqual(Ok(4), Ok(2) * Ok(2))

        v1 = Ok(2)
        v2 = Err('err')

        self.assertEqual(v1 & v2, v1.bool_and(v2))
        self.assertEqual(v1 | v2, v1.bool_or(v2))

    def test_catch(self):
        def maybe_error(v: int) -> int:
            if v % 2 == 0:
                return v + 1
            else:
                raise ValueError()

        self.assertEqual(
            Result.catch(lambda: maybe_error(2)),
            Result.of_ok(3),
        )
        self.assertIsInstance(
            Result.catch(lambda: maybe_error(3)).unwrap_err(),
            ValueError,
        )

        self.assertEqual(
            Result.catch_from(maybe_error, v=2),
            Result.of_ok(3),
        )
        self.assertIsInstance(
            Result.catch_from(maybe_error, 3).unwrap_err(),
            ValueError,
        )

    def test_into_option(self):
        self.assertEqual(
            Result.of_ok(2).ok(),
            Option.some(2),
        )
        self.assertEqual(
            Result.of_err("err").ok(),
            Option.none(),
        )

        self.assertEqual(
            Result.of_err("err").err(),
            Option.some("err"),
        )
        self.assertEqual(
            Result.of_ok(0).err(),
            Option.none(),
        )

    def test_mapping(self):
        self.assertEqual(
            Result.of_ok(2).map(lambda x: x * 2),
            Result.of_ok(4),
        )
        self.assertEqual(
            Result.of_err("err").map(lambda x: x * 2),
            Result.of_err("err"),
        )

        self.assertEqual(Result.of_ok("foo").map_or(42, lambda s: len(s)), 3)
        self.assertEqual(
            Result.of_err("bar").map_or(42, lambda s: len(s)),
            42,
        )

        self.assertEqual(
            Result.of_ok("foo").map_or_else(lambda e: len(e) + 3, lambda v: len(v)),
            3,
        )
        self.assertEqual(
            Result.of_err("bar").map_or_else(lambda e: len(e) + 3, lambda v: len(v)),
            6,
        )

        self.assertEqual(
            Result.of_ok(2).map_err(lambda x: str(x)),
            Result.of_ok(2),
        )
        self.assertEqual(
            Result.of_err(-1).map_err(lambda x: str(x)),
            Result.of_err("-1"),
        )
        class Test:
            value: int
            def __init__(self, val: int):
                self.value = val

            def change_value(self, new_value: int):
                print('old:', self.value, 'new:', new_value)
                self.value = new_value

        maybe_ok = Result.of_ok(Test(1))
        self.assertEqual(maybe_ok.unwrap().value, 1)
        maybe_ok.map_mut(lambda x: x.change_value(5))
        self.assertEqual(maybe_ok.unwrap().value, 5)

        maybe_ok = Result.of_err(Test(1))
        self.assertEqual(maybe_ok.unwrap_err().value, 1)
        maybe_ok.map_err_mut(lambda x: x.change_value(5))
        self.assertEqual(maybe_ok.unwrap_err().value, 5)

    def test_inspect(self):
        k = []
        Result.of_ok(2).inspect(lambda x: k.append(x))
        self.assertListEqual(k, [2])
        Result.of_err("err").inspect(lambda x: k.append(x))
        self.assertListEqual(k, [2])

        k = []
        Result.of_ok(2).inspect_err(lambda x: k.append(x))
        self.assertListEqual(k, [])
        Result.of_err(-1).inspect_err(lambda x: k.append(x))
        self.assertListEqual(k, [-1])

    def test_to_array(self):
        self.assertListEqual(Result.of_ok(2).to_array(), [2])
        self.assertListEqual(Result.of_err("err").to_array(), [])

    def test_unwrap(self):
        self.assertEqual(Result.of_ok(2).expect("error"), 2)
        try:
            Result.of_err("err").expect("error")
        except UnwrapException as e:
            self.assertEqual(str(e), "ResultError: error: 'err'")

        self.assertEqual(Result.of_err("err").expect_err("ok"), "err")
        try:
            Result.of_ok(2).expect_err("ok")
        except UnwrapException as e:
            self.assertEqual(str(e), "ResultError: ok: 2")

        self.assertEqual(Result.of_ok(2).unwrap(), 2)
        try:
            Result.of_err("err").unwrap()
        except UnwrapException as e:
            self.assertEqual(
                str(e),
                "ResultError: call `Result.unwrap` on an `Err` value: 'err'",
            )

        self.assertEqual(Result.of_err("err").unwrap_err(), "err")
        try:
            Result.of_ok(2).unwrap_err()
        except UnwrapException as e:
            self.assertEqual(
                str(e),
                "ResultError: call `Result.unwrap_err` on an `Ok` value: 2",
            )

        self.assertEqual(Result.of_ok(9).unwrap_or(2), 9)
        self.assertEqual(Result.of_err("err").unwrap_or(2), 2)

        self.assertEqual(Result.of_ok(2).unwrap_or_else(lambda s: len(s)), 2)
        self.assertEqual(
            Result.of_err("foo").unwrap_or_else(lambda s: len(s)),
            3,
        )

        self.assertEqual(Result.of_ok("foo").unwrap_unchecked(),
                         Result.of_err("foo").unwrap_unchecked())

        self.assertEqual(Result.OK, True)
        self.assertEqual(Result.ERR, False)
        self.assertTupleEqual(Ok(3).to_pattern(), (Result.OK, 3))
        self.assertTupleEqual(Err(3).to_pattern(), (Result.ERR, 3))

    def test_bool(self):
        self.assertEqual(
            Result.of_ok(2).bool_and(Result.of_err("late error")),
            Result.of_err("late error"),
        )
        self.assertEqual(
            Result.of_err("early error").bool_and(Result.of_ok(2)),
            Result.of_err("early error"),
        )
        self.assertEqual(
            Result.of_err("early error").bool_and(Result.of_err("late error")),
            Result.of_err("early error"),
        )
        self.assertEqual(
            Result.of_ok(2).bool_and(Result.of_ok("another ok")),
            Result.of_ok("another ok"),
        )

        self.assertEqual(
            Result.of_ok(2).bool_or(Result.of_err("late error")),
            Result.of_ok(2),
        )
        self.assertEqual(
            Result.of_err("early error").bool_or(Result.of_ok(2)),
            Result.of_ok(2),
        )
        self.assertEqual(
            Result.of_err("early error").bool_or(Result.of_err("late error")),
            Result.of_err("late error"),
        )
        self.assertEqual(
            Result.of_ok(2).bool_or(Result.of_ok(100)),
            Result.of_ok(2),
        )

    def test_chain(self):
        self.assertEqual(
            Result.of_ok(2).and_then(lambda n: Result.of_ok(n * 2)),
            Result.of_ok(4),
        )
        self.assertEqual(
            Result.of_ok(2).and_then(lambda _: Result.of_err("err")),
            Result.of_err("err"),
        )
        self.assertEqual(
            Result.of_err("err").and_then(lambda n: Result.of_ok(n * 2)),
            Result.of_err("err"),
        )

        def square(v: int) -> Result[int, int]:
            return Result.of_ok(v * v)

        def err(v: int) -> Result[int, int]:
            return Result.of_err(v)

        x: Result[int, int] = Result.of_ok(2)
        self.assertEqual(
            x.or_else(square).or_else(square),
            Result.of_ok(2),
        )
        self.assertEqual(
            x.or_else(err).or_else(square),
            Result.of_ok(2),
        )

        x: Result[int, int] = Result.of_err(3)
        self.assertEqual(
            x.or_else(square).or_else(err),
            Result.of_ok(9),
        )
        self.assertEqual(
            x.or_else(err).or_else(err),
            Result.of_err(3),
        )

    def test_transpose(self):
        x = Result.of_ok(Option.some(5))
        y = Option.some(Result.of_ok(5))
        self.assertEqual(x.transpose(), y)

    def test_flatten(self):
        self.assertEqual(
            Result.of_ok("hello"),
            Result.of_ok(Result.of_ok("hello")).flatten(),
        )
        self.assertEqual(
            Result.of_err(6),
            Result.of_ok(Result.of_err(6)).flatten(),
        )
        self.assertEqual(
            Result.of_err(5),
            Result.of_err(5).flatten(),
        )
        x = Result.of_ok(Result.of_ok(Result.of_ok("hello")))
        self.assertEqual(
            Result.of_ok(Result.of_ok("hello")),
            x.flatten(),
        )
        self.assertEqual(
            Result.of_ok("hello"),
            x.flatten().flatten(),
        )


if __name__ == "__main__":
    unittest.main()
