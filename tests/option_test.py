import unittest

import monad_std


class OptionTest(unittest.TestCase):
    def test_build(self):
        self.assertEqual(monad_std.Option.from_nullable(None), monad_std.Option.none())
        self.assertEqual(monad_std.Option.from_nullable(2), monad_std.Option.some(2))

    def test_identify(self):
        x: monad_std.Option[int] = monad_std.Option.some(2)
        self.assertTrue(x.is_some())
        self.assertFalse(x.is_none())
        x: monad_std.Option[int] = monad_std.Option.none()
        self.assertFalse(x.is_some())
        self.assertTrue(x.is_none())

        x: monad_std.Option[int] = monad_std.Option.some(2)
        self.assertTrue(x.is_some_and(lambda v: v > 1))
        x: monad_std.Option[int] = monad_std.Option.some(0)
        self.assertFalse(x.is_some_and(lambda v: v > 1))
        x: monad_std.Option[int] = monad_std.Option.none()
        self.assertFalse(x.is_some_and(lambda v: v > 1))

    def test_magic_method(self):
        self.assertTrue(monad_std.Option.some(2))
        self.assertFalse(monad_std.Option.none())

        self.assertEqual(monad_std.Option.some(2), monad_std.Option.some(1) + monad_std.Option.some(1))

        self.assertEqual(monad_std.Option.some(4), monad_std.Option.some(2) * monad_std.Option.some(2))

        self.assertEqual(hash(monad_std.Option.some(2)), hash(2))

        v1 = monad_std.Option.some(2)
        v2 = monad_std.Option.some(4)

        self.assertEqual(v1 & v2, v1.bool_and(v2))
        self.assertEqual(v1 | v2, v1.bool_or(v2))
        self.assertEqual(v1 ^ v2, v1.bool_xor(v2))

    def test_unwrap(self):
        x: monad_std.Option[str] = monad_std.Option.some("value")
        self.assertEqual(x.expect("hey, this is an `Option::None` object"), "value")
        x: monad_std.Option[str] = monad_std.Option.none()
        try:
            x.expect("hey, this is an `Option::None` object")
        except monad_std.UnwrapException as e:
            self.assertEqual(str(e), "OptionError: hey, this is an `Option::None` object")

        x: monad_std.Option[str] = monad_std.Option.some("air")
        self.assertEqual(x.unwrap(), "air")
        x: monad_std.Option[str] = monad_std.Option.none()
        try:
            x.unwrap()
        except monad_std.UnwrapException as e:
            self.assertEqual(
                str(e),
                "OptionError: call `Option.unwrap` on an " "`Option::None` object",
            )

        self.assertEqual(monad_std.Option.some("car").unwrap_or("bike"), "car")
        self.assertEqual(monad_std.Option.none().unwrap_or("bike"), "bike")

        k = 10
        self.assertEqual(monad_std.Option.some(4).unwrap_or_else(lambda: 2 * k), 4)
        self.assertEqual(monad_std.Option.none().unwrap_or_else(lambda: 2 * k), 20)

        self.assertEqual(monad_std.Option.some(4).unwrap_unchecked(), 4)
        self.assertTrue(monad_std.Option.none().unwrap_unchecked() is None)

        self.assertEqual(monad_std.Option.some(4).to_pattern(), 4)
        self.assertTrue(monad_std.Option.none().to_pattern() is None)

        x: monad_std.Option[str] = monad_std.Option.some("air")
        self.assertEqual(x.to_nullable(), "air")
        x: monad_std.Option[str] = monad_std.Option.none()
        self.assertIsNone(x.to_nullable())
        x: monad_std.Option[None] = monad_std.Option.some(None)
        self.assertIsNone(x.to_nullable())

    def test_map(self):
        x = []
        monad_std.Option.some(2).inspect(lambda s: x.append(s))
        self.assertListEqual(x, [2])
        monad_std.Option.none().inspect(lambda s: x.append(s))
        self.assertListEqual(x, [2])

        maybe_some_string = monad_std.Option.some("Hello, World!")
        maybe_some_len = maybe_some_string.map(lambda s: len(s))
        self.assertEqual(maybe_some_len, monad_std.Option.some(13))
        self.assertEqual(
            monad_std.Option.none().map(lambda s: len(s)),
            monad_std.Option.none(),
        )

        self.assertEqual(
            monad_std.Option.some("foo").map_or(42, lambda s: len(s)),
            3,
        )
        self.assertEqual(monad_std.Option.none().map_or(42, lambda s: len(s)), 42)

        k = 21
        self.assertEqual(
            monad_std.Option.some("bar").map_or_else(lambda: 2 * k, lambda s: len(s)),
            3,
        )
        self.assertEqual(
            monad_std.Option.none().map_or_else(lambda: 2 * k, lambda s: len(s)),
            42,
        )
        class Test:
            val: int
            def __init__(self, val: int):
                self.val = val

            def change_value(self, new_value: int):
                self.val = new_value

        maybe_something = monad_std.Option.some(Test(1))
        self.assertEqual(maybe_something.unwrap().val, 1)
        maybe_something.map_mut(lambda x: x.change_value(5))
        self.assertEqual(maybe_something.unwrap().val, 5)

    def test_into_result(self):
        self.assertEqual(
            monad_std.Option.some("foo").ok_or(0),
            monad_std.Result.of_ok("foo"),
        )
        self.assertEqual(
            monad_std.Option.none().ok_or(0),
            monad_std.Result.of_err(0),
        )

        k = 21
        self.assertEqual(
            monad_std.Option.some("foo").ok_or_else(lambda: k * 2),
            monad_std.Result.of_ok("foo"),
        )
        self.assertEqual(
            monad_std.Option.none().ok_or_else(lambda: k * 2),
            monad_std.Result.of_err(42),
        )

    def test_to_array(self):
        self.assertListEqual(monad_std.Option.some(1).to_array(), [1])
        self.assertListEqual(monad_std.Option.none().to_array(), [])

    def test_bool_eval(self):
        self.assertEqual(
            monad_std.Option.some(2).bool_and(monad_std.Option.none()),
            monad_std.Option.none(),
        )
        self.assertEqual(
            monad_std.Option.none().bool_and(monad_std.Option.some("foo")),
            monad_std.Option.none(),
        )
        self.assertEqual(
            monad_std.Option.some(2).bool_and(monad_std.Option.some("bar")),
            monad_std.Option.some("bar"),
        )
        self.assertEqual(
            monad_std.Option.none().bool_and(monad_std.Option.none()),
            monad_std.Option.none(),
        )

        self.assertEqual(
            monad_std.Option.some(2).bool_or(monad_std.Option.none()),
            monad_std.Option.some(2),
        )
        self.assertEqual(
            monad_std.Option.none().bool_or(monad_std.Option.some(100)),
            monad_std.Option.some(100),
        )
        self.assertEqual(
            monad_std.Option.some(2).bool_or(monad_std.Option.some(100)),
            monad_std.Option.some(2),
        )
        self.assertEqual(
            monad_std.Option.none().bool_or(monad_std.Option.none()),
            monad_std.Option.none(),
        )

        self.assertEqual(
            monad_std.Option.some(2).bool_xor(monad_std.Option.none()),
            monad_std.Option.some(2),
        )
        self.assertEqual(
            monad_std.Option.none().bool_xor(monad_std.Option.some(2)),
            monad_std.Option.some(2),
        )
        self.assertEqual(
            monad_std.Option.some(2).bool_xor(monad_std.Option.some(2)),
            monad_std.Option.none(),
        )
        self.assertEqual(
            monad_std.Option.none().bool_xor(monad_std.Option.none()),
            monad_std.Option.none(),
        )

    def test_chain(self):
        self.assertEqual(
            monad_std.Option.some(2).and_then(lambda x: monad_std.Option.some(str(x))),
            monad_std.Option.some("2"),
        )
        self.assertEqual(
            monad_std.Option.some(10).and_then(lambda _: monad_std.Option.none()),
            monad_std.Option.none(),
        )
        self.assertEqual(
            monad_std.Option.none().and_then(lambda x: monad_std.Option.some(str(x))),
            monad_std.Option.none(),
        )

        def get_from(l, i):
            try:
                return monad_std.Option.some(l[i])
            except IndexError:
                return monad_std.Option.none()

        arr2d = [["A0", "A1"], ["B0", "B1"]]
        self.assertEqual(
            get_from(arr2d, 0).and_then(lambda row: get_from(row, 1)),
            monad_std.Option.some("A1"),
        )
        self.assertEqual(
            get_from(arr2d, 2).and_then(lambda row: get_from(row, 0)),
            monad_std.Option.none(),
        )

        self.assertEqual(
            monad_std.Option.some("foo").or_else(lambda: monad_std.Option.some("bar")),
            monad_std.Option.some("foo"),
        )
        self.assertEqual(
            monad_std.Option.none().or_else(lambda: monad_std.Option.some("bar")),
            monad_std.Option.some("bar"),
        )
        self.assertEqual(
            monad_std.Option.none().or_else(lambda: monad_std.Option.none()),
            monad_std.Option.none(),
        )

        self.assertEqual(
            monad_std.Option.none().filter(lambda n: n % 2 == 0),
            monad_std.Option.none(),
        )
        self.assertEqual(
            monad_std.Option.some(3).filter(lambda n: n % 2 == 0),
            monad_std.Option.none(),
        )
        self.assertEqual(
            monad_std.Option.some(4).filter(lambda n: n % 2 == 0),
            monad_std.Option.some(4),
        )

        self.assertEqual(
            monad_std.Option.some(1).zip(monad_std.Option.some("hi")),
            monad_std.Option.some((1, "hi")),
        )
        self.assertEqual(
            monad_std.Option.some(1).zip(monad_std.Option.none()),
            monad_std.Option.none(),
        )

        def make_point(x, y):
            return monad_std.Option.some({"x": x, "y": y})

        self.assertEqual(
            monad_std.Option.some(2).zip_with(monad_std.Option.some(4), make_point),
            monad_std.Option.some({"x": 2, "y": 4}),
        )
        self.assertEqual(
            monad_std.Option.some(2).zip_with(monad_std.Option.none(), make_point),
            monad_std.Option.none(),
        )

    def test_unzip(self):
        self.assertTupleEqual(
            monad_std.Option.some((1, "hi")).unzip(),
            (
                monad_std.Option.some(1),
                monad_std.Option.some("hi"),
            ),
        )
        self.assertTupleEqual(
            monad_std.Option.none().unzip(),
            (
                monad_std.Option.none(),
                monad_std.Option.none(),
            ),
        )

    def test_transpose(self):
        x = monad_std.Result.of_ok(monad_std.Option.some(5))
        y = monad_std.Option.some(monad_std.Result.of_ok(5))
        self.assertEqual(x, y.transpose())

    def test_flatten(self):
        self.assertEqual(
            monad_std.Option.some(monad_std.Option.some(6)).flatten(),
            monad_std.Option.some(6),
        )
        self.assertEqual(
            monad_std.Option.some(monad_std.Option.none()).flatten(),
            monad_std.Option.none(),
        )
        self.assertEqual(
            monad_std.Option.none().flatten(),
            monad_std.Option.none(),
        )
        self.assertEqual(
            monad_std.Option.some(monad_std.Option.some(monad_std.Option.some(6))).flatten(),
            monad_std.Option.some(monad_std.Option.some(6)),
        )
        self.assertEqual(
            monad_std.Option.some(monad_std.Option.some(monad_std.Option.some(6))).flatten().flatten(),
            monad_std.Option.some(6),
        )


if __name__ == "__main__":
    unittest.main()
