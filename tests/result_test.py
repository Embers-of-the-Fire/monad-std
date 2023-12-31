import unittest

import monad_std


class ResultTest(unittest.TestCase):
    def test_identify(self):
        self.assertTrue(monad_std.Result.of_ok(2).is_ok())
        self.assertFalse(monad_std.Result.of_ok(2).is_err())
        self.assertFalse(monad_std.Result.of_err("err").is_ok())
        self.assertTrue(monad_std.Result.of_err("err").is_err())

        self.assertTrue(monad_std.Result.of_ok(2).is_ok_and(lambda x: x > 1))
        self.assertFalse(monad_std.Result.of_ok(0).is_ok_and(lambda x: x > 1))
        self.assertFalse(monad_std.Result.of_err("error").is_ok_and(lambda x: x > 1))

        self.assertFalse(monad_std.Result.of_ok(2).is_err_and(lambda x: len(x) == 3))
        self.assertTrue(monad_std.Result.of_err("err").is_err_and(lambda x: len(x) == 3))
        self.assertFalse(monad_std.Result.of_err("error").is_err_and(lambda x: len(x) == 3))

    def test_magic_method(self):
        self.assertTrue(monad_std.Ok(2))
        self.assertFalse(monad_std.Err("err"))

        self.assertEqual(monad_std.Ok(2), monad_std.Ok(1) + monad_std.Ok(1))

        self.assertEqual(monad_std.Ok(4), monad_std.Ok(2) * monad_std.Ok(2))

        v1 = monad_std.Ok(2)
        v2 = monad_std.Err('err')

        self.assertEqual(v1 & v2, v1.bool_and(v2))
        self.assertEqual(v1 | v2, v1.bool_or(v2))

    def test_catch(self):
        def maybe_error(v: int) -> int:
            if v % 2 == 0:
                return v + 1
            else:
                raise ValueError()

        self.assertEqual(
            monad_std.Result.catch(lambda: maybe_error(2)),
            monad_std.Result.of_ok(3),
        )
        self.assertIsInstance(
            monad_std.Result.catch(lambda: maybe_error(3)).unwrap_err(),
            ValueError,
        )

        self.assertEqual(
            monad_std.Result.catch_from(maybe_error, v=2),
            monad_std.Result.of_ok(3),
        )
        self.assertIsInstance(
            monad_std.Result.catch_from(maybe_error, 3).unwrap_err(),
            ValueError,
        )

    def test_into_option(self):
        self.assertEqual(
            monad_std.Result.of_ok(2).ok(),
            monad_std.Option.some(2),
        )
        self.assertEqual(
            monad_std.Result.of_err("err").ok(),
            monad_std.Option.none(),
        )

        self.assertEqual(
            monad_std.Result.of_err("err").err(),
            monad_std.Option.some("err"),
        )
        self.assertEqual(
            monad_std.Result.of_ok(0).err(),
            monad_std.Option.none(),
        )

    def test_mapping(self):
        self.assertEqual(
            monad_std.Result.of_ok(2).map(lambda x: x * 2),
            monad_std.Result.of_ok(4),
        )
        self.assertEqual(
            monad_std.Result.of_err("err").map(lambda x: x * 2),
            monad_std.Result.of_err("err"),
        )

        self.assertEqual(monad_std.Result.of_ok("foo").map_or(42, lambda s: len(s)), 3)
        self.assertEqual(
            monad_std.Result.of_err("bar").map_or(42, lambda s: len(s)),
            42,
        )

        self.assertEqual(
            monad_std.Result.of_ok("foo").map_or_else(lambda e: len(e) + 3, lambda v: len(v)),
            3,
        )
        self.assertEqual(
            monad_std.Result.of_err("bar").map_or_else(lambda e: len(e) + 3, lambda v: len(v)),
            6,
        )

        self.assertEqual(
            monad_std.Result.of_ok(2).map_err(lambda x: str(x)),
            monad_std.Result.of_ok(2),
        )
        self.assertEqual(
            monad_std.Result.of_err(-1).map_err(lambda x: str(x)),
            monad_std.Result.of_err("-1"),
        )
        class Test:
            value: int
            def __init__(self, val: int):
                self.value = val

            def change_value(self, new_value: int):
                print('old:', self.value, 'new:', new_value)
                self.value = new_value

        maybe_ok = monad_std.Result.of_ok(Test(1))
        self.assertEqual(maybe_ok.unwrap().value, 1)
        maybe_ok.map_mut(lambda x: x.change_value(5))
        self.assertEqual(maybe_ok.unwrap().value, 5)

        maybe_ok = monad_std.Result.of_err(Test(1))
        self.assertEqual(maybe_ok.unwrap_err().value, 1)
        maybe_ok.map_err_mut(lambda x: x.change_value(5))
        self.assertEqual(maybe_ok.unwrap_err().value, 5)

    def test_inspect(self):
        k = []
        monad_std.Result.of_ok(2).inspect(lambda x: k.append(x))
        self.assertListEqual(k, [2])
        monad_std.Result.of_err("err").inspect(lambda x: k.append(x))
        self.assertListEqual(k, [2])

        k = []
        monad_std.Result.of_ok(2).inspect_err(lambda x: k.append(x))
        self.assertListEqual(k, [])
        monad_std.Result.of_err(-1).inspect_err(lambda x: k.append(x))
        self.assertListEqual(k, [-1])

    def test_to_array(self):
        self.assertListEqual(monad_std.Result.of_ok(2).to_array(), [2])
        self.assertListEqual(monad_std.Result.of_err("err").to_array(), [])

    def test_unwrap(self):
        self.assertEqual(monad_std.Result.of_ok(2).expect("error"), 2)
        try:
            monad_std.Result.of_err("err").expect("error")
        except monad_std.UnwrapException as e:
            self.assertEqual(str(e), "ResultError: error: 'err'")

        self.assertEqual(monad_std.Result.of_err("err").expect_err("ok"), "err")
        try:
            monad_std.Result.of_ok(2).expect_err("ok")
        except monad_std.UnwrapException as e:
            self.assertEqual(str(e), "ResultError: ok: 2")

        self.assertEqual(monad_std.Result.of_ok(2).unwrap(), 2)
        try:
            monad_std.Result.of_err("err").unwrap()
        except monad_std.UnwrapException as e:
            self.assertEqual(
                str(e),
                "ResultError: call `Result.unwrap` on an `Err` value: 'err'",
            )

        self.assertEqual(monad_std.Result.of_err("err").unwrap_err(), "err")
        try:
            monad_std.Result.of_ok(2).unwrap_err()
        except monad_std.UnwrapException as e:
            self.assertEqual(
                str(e),
                "ResultError: call `Result.unwrap_err` on an `Ok` value: 2",
            )

        self.assertEqual(monad_std.Result.of_ok(9).unwrap_or(2), 9)
        self.assertEqual(monad_std.Result.of_err("err").unwrap_or(2), 2)

        self.assertEqual(monad_std.Result.of_ok(2).unwrap_or_else(lambda s: len(s)), 2)
        self.assertEqual(
            monad_std.Result.of_err("foo").unwrap_or_else(lambda s: len(s)),
            3,
        )

        self.assertEqual(monad_std.Result.of_ok("foo").unwrap_unchecked(),
                         monad_std.Result.of_err("foo").unwrap_unchecked())

        self.assertEqual(monad_std.Result.OK, True)
        self.assertEqual(monad_std.Result.ERR, False)
        self.assertTupleEqual(monad_std.Ok(3).to_pattern(), (monad_std.Result.OK, 3))
        self.assertTupleEqual(monad_std.Err(3).to_pattern(), (monad_std.Result.ERR, 3))

    def test_bool(self):
        self.assertEqual(
            monad_std.Result.of_ok(2).bool_and(monad_std.Result.of_err("late error")),
            monad_std.Result.of_err("late error"),
        )
        self.assertEqual(
            monad_std.Result.of_err("early error").bool_and(monad_std.Result.of_ok(2)),
            monad_std.Result.of_err("early error"),
        )
        self.assertEqual(
            monad_std.Result.of_err("early error").bool_and(monad_std.Result.of_err("late error")),
            monad_std.Result.of_err("early error"),
        )
        self.assertEqual(
            monad_std.Result.of_ok(2).bool_and(monad_std.Result.of_ok("another ok")),
            monad_std.Result.of_ok("another ok"),
        )

        self.assertEqual(
            monad_std.Result.of_ok(2).bool_or(monad_std.Result.of_err("late error")),
            monad_std.Result.of_ok(2),
        )
        self.assertEqual(
            monad_std.Result.of_err("early error").bool_or(monad_std.Result.of_ok(2)),
            monad_std.Result.of_ok(2),
        )
        self.assertEqual(
            monad_std.Result.of_err("early error").bool_or(monad_std.Result.of_err("late error")),
            monad_std.Result.of_err("late error"),
        )
        self.assertEqual(
            monad_std.Result.of_ok(2).bool_or(monad_std.Result.of_ok(100)),
            monad_std.Result.of_ok(2),
        )

    def test_chain(self):
        self.assertEqual(
            monad_std.Result.of_ok(2).and_then(lambda n: monad_std.Result.of_ok(n * 2)),
            monad_std.Result.of_ok(4),
        )
        self.assertEqual(
            monad_std.Result.of_ok(2).and_then(lambda _: monad_std.Result.of_err("err")),
            monad_std.Result.of_err("err"),
        )
        self.assertEqual(
            monad_std.Result.of_err("err").and_then(lambda n: monad_std.Result.of_ok(n * 2)),
            monad_std.Result.of_err("err"),
        )

        def square(v: int) -> monad_std.Result[int, int]:
            return monad_std.Result.of_ok(v * v)

        def err(v: int) -> monad_std.Result[int, int]:
            return monad_std.Result.of_err(v)

        x: monad_std.Result[int, int] = monad_std.Result.of_ok(2)
        self.assertEqual(
            x.or_else(square).or_else(square),
            monad_std.Result.of_ok(2),
        )
        self.assertEqual(
            x.or_else(err).or_else(square),
            monad_std.Result.of_ok(2),
        )

        x: monad_std.Result[int, int] = monad_std.Result.of_err(3)
        self.assertEqual(
            x.or_else(square).or_else(err),
            monad_std.Result.of_ok(9),
        )
        self.assertEqual(
            x.or_else(err).or_else(err),
            monad_std.Result.of_err(3),
        )

    def test_transpose(self):
        x = monad_std.Result.of_ok(monad_std.Option.some(5))
        y = monad_std.Option.some(monad_std.Result.of_ok(5))
        self.assertEqual(x.transpose(), y)

    def test_flatten(self):
        self.assertEqual(
            monad_std.Result.of_ok("hello"),
            monad_std.Result.of_ok(monad_std.Result.of_ok("hello")).flatten(),
        )
        self.assertEqual(
            monad_std.Result.of_err(6),
            monad_std.Result.of_ok(monad_std.Result.of_err(6)).flatten(),
        )
        self.assertEqual(
            monad_std.Result.of_err(5),
            monad_std.Result.of_err(5).flatten(),
        )
        x = monad_std.Result.of_ok(monad_std.Result.of_ok(monad_std.Result.of_ok("hello")))
        self.assertEqual(
            monad_std.Result.of_ok(monad_std.Result.of_ok("hello")),
            x.flatten(),
        )
        self.assertEqual(
            monad_std.Result.of_ok("hello"),
            x.flatten().flatten(),
        )


if __name__ == "__main__":
    unittest.main()
