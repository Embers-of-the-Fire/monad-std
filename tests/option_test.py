import unittest

from monad_std.prelude import *
from monad_std import UnwrapException


class OptionTest(unittest.TestCase):
    def test_build(self):
        self.assertEqual(Option.from_nullable(None), Option.none())
        self.assertEqual(Option.from_nullable(2), Option.some(2))

    def test_identify(self):
        x: Option[int] = Option.some(2)
        self.assertTrue(x.is_some())
        self.assertFalse(x.is_none())
        x: Option[int] = Option.none()
        self.assertFalse(x.is_some())
        self.assertTrue(x.is_none())

        x: Option[int] = Option.some(2)
        self.assertTrue(x.is_some_and(lambda v: v > 1))
        x: Option[int] = Option.some(0)
        self.assertFalse(x.is_some_and(lambda v: v > 1))
        x: Option[int] = Option.none()
        self.assertFalse(x.is_some_and(lambda v: v > 1))

    def test_magic_method(self):
        self.assertTrue(Option.some(2))
        self.assertFalse(Option.none())

        self.assertEqual(Option.some(2), Option.some(1) + Option.some(1))

        self.assertEqual(Option.some(4), Option.some(2) * Option.some(2))

        self.assertEqual(hash(Option.some(2)), hash(2))

        v1 = Option.some(2)
        v2 = Option.some(4)

        self.assertEqual(v1 & v2, v1.bool_and(v2))
        self.assertEqual(v1 | v2, v1.bool_or(v2))
        self.assertEqual(v1 ^ v2, v1.bool_xor(v2))

    def test_unwrap(self):
        x: Option[str] = Option.some("value")
        self.assertEqual(x.expect("hey, this is an `Option::None` object"), "value")
        x: Option[str] = Option.none()
        try:
            x.expect("hey, this is an `Option::None` object")
        except UnwrapException as e:
            self.assertEqual(str(e), "OptionError: hey, this is an `Option::None` object")

        x: Option[str] = Option.some("air")
        self.assertEqual(x.unwrap(), "air")
        x: Option[str] = Option.none()
        try:
            x.unwrap()
        except UnwrapException as e:
            self.assertEqual(
                str(e),
                "OptionError: call `Option.unwrap` on an " "`Option::None` object",
            )

        self.assertEqual(Option.some("car").unwrap_or("bike"), "car")
        self.assertEqual(Option.none().unwrap_or("bike"), "bike")

        k = 10
        self.assertEqual(Option.some(4).unwrap_or_else(lambda: 2 * k), 4)
        self.assertEqual(Option.none().unwrap_or_else(lambda: 2 * k), 20)

        self.assertEqual(Option.some(4).unwrap_unchecked(), 4)
        self.assertTrue(Option.none().unwrap_unchecked() is None)

        self.assertEqual(Option.some(4).to_pattern(), 4)
        self.assertTrue(Option.none().to_pattern() is None)

        x: Option[str] = Option.some("air")
        self.assertEqual(x.to_nullable(), "air")
        x: Option[str] = Option.none()
        self.assertIsNone(x.to_nullable())
        x: Option[None] = Option.some(None)
        self.assertIsNone(x.to_nullable())

    def test_map(self):
        x = []
        Option.some(2).inspect(lambda s: x.append(s))
        self.assertListEqual(x, [2])
        Option.none().inspect(lambda s: x.append(s))
        self.assertListEqual(x, [2])

        maybe_some_string = Option.some("Hello, World!")
        maybe_some_len = maybe_some_string.map(lambda s: len(s))
        self.assertEqual(maybe_some_len, Option.some(13))
        self.assertEqual(
            Option.none().map(lambda s: len(s)),
            Option.none(),
        )

        self.assertEqual(
            Option.some("foo").map_or(42, lambda s: len(s)),
            3,
        )
        self.assertEqual(Option.none().map_or(42, lambda s: len(s)), 42)

        k = 21
        self.assertEqual(
            Option.some("bar").map_or_else(lambda: 2 * k, lambda s: len(s)),
            3,
        )
        self.assertEqual(
            Option.none().map_or_else(lambda: 2 * k, lambda s: len(s)),
            42,
        )
        class Test:
            val: int
            def __init__(self, val: int):
                self.val = val

            def change_value(self, new_value: int):
                self.val = new_value

        maybe_something = Option.some(Test(1))
        self.assertEqual(maybe_something.unwrap().val, 1)
        maybe_something.map_mut(lambda x: x.change_value(5))
        self.assertEqual(maybe_something.unwrap().val, 5)

    def test_into_result(self):
        self.assertEqual(
            Option.some("foo").ok_or(0),
            Result.of_ok("foo"),
        )
        self.assertEqual(
            Option.none().ok_or(0),
            Result.of_err(0),
        )

        k = 21
        self.assertEqual(
            Option.some("foo").ok_or_else(lambda: k * 2),
            Result.of_ok("foo"),
        )
        self.assertEqual(
            Option.none().ok_or_else(lambda: k * 2),
            Result.of_err(42),
        )

    def test_to_array(self):
        self.assertListEqual(Option.some(1).to_array(), [1])
        self.assertListEqual(Option.none().to_array(), [])

    def test_bool_eval(self):
        self.assertEqual(
            Option.some(2).bool_and(Option.none()),
            Option.none(),
        )
        self.assertEqual(
            Option.none().bool_and(Option.some("foo")),
            Option.none(),
        )
        self.assertEqual(
            Option.some(2).bool_and(Option.some("bar")),
            Option.some("bar"),
        )
        self.assertEqual(
            Option.none().bool_and(Option.none()),
            Option.none(),
        )

        self.assertEqual(
            Option.some(2).bool_or(Option.none()),
            Option.some(2),
        )
        self.assertEqual(
            Option.none().bool_or(Option.some(100)),
            Option.some(100),
        )
        self.assertEqual(
            Option.some(2).bool_or(Option.some(100)),
            Option.some(2),
        )
        self.assertEqual(
            Option.none().bool_or(Option.none()),
            Option.none(),
        )

        self.assertEqual(
            Option.some(2).bool_xor(Option.none()),
            Option.some(2),
        )
        self.assertEqual(
            Option.none().bool_xor(Option.some(2)),
            Option.some(2),
        )
        self.assertEqual(
            Option.some(2).bool_xor(Option.some(2)),
            Option.none(),
        )
        self.assertEqual(
            Option.none().bool_xor(Option.none()),
            Option.none(),
        )

    def test_chain(self):
        self.assertEqual(
            Option.some(2).and_then(lambda x: Option.some(str(x))),
            Option.some("2"),
        )
        self.assertEqual(
            Option.some(10).and_then(lambda _: Option.none()),
            Option.none(),
        )
        self.assertEqual(
            Option.none().and_then(lambda x: Option.some(str(x))),
            Option.none(),
        )

        def get_from(l, i):
            try:
                return Option.some(l[i])
            except IndexError:
                return Option.none()

        arr2d = [["A0", "A1"], ["B0", "B1"]]
        self.assertEqual(
            get_from(arr2d, 0).and_then(lambda row: get_from(row, 1)),
            Option.some("A1"),
        )
        self.assertEqual(
            get_from(arr2d, 2).and_then(lambda row: get_from(row, 0)),
            Option.none(),
        )

        self.assertEqual(
            Option.some("foo").or_else(lambda: Option.some("bar")),
            Option.some("foo"),
        )
        self.assertEqual(
            Option.none().or_else(lambda: Option.some("bar")),
            Option.some("bar"),
        )
        self.assertEqual(
            Option.none().or_else(lambda: Option.none()),
            Option.none(),
        )

        self.assertEqual(
            Option.none().filter(lambda n: n % 2 == 0),
            Option.none(),
        )
        self.assertEqual(
            Option.some(3).filter(lambda n: n % 2 == 0),
            Option.none(),
        )
        self.assertEqual(
            Option.some(4).filter(lambda n: n % 2 == 0),
            Option.some(4),
        )

        self.assertEqual(
            Option.some(1).zip(Option.some("hi")),
            Option.some((1, "hi")),
        )
        self.assertEqual(
            Option.some(1).zip(Option.none()),
            Option.none(),
        )

        def make_point(x, y):
            return Option.some({"x": x, "y": y})

        self.assertEqual(
            Option.some(2).zip_with(Option.some(4), make_point),
            Option.some({"x": 2, "y": 4}),
        )
        self.assertEqual(
            Option.some(2).zip_with(Option.none(), make_point),
            Option.none(),
        )

    def test_unzip(self):
        self.assertTupleEqual(
            Option.some((1, "hi")).unzip(),
            (
                Option.some(1),
                Option.some("hi"),
            ),
        )
        self.assertTupleEqual(
            Option.none().unzip(),
            (
                Option.none(),
                Option.none(),
            ),
        )

    def test_transpose(self):
        x = Result.of_ok(Option.some(5))
        y = Option.some(Result.of_ok(5))
        self.assertEqual(x, y.transpose())

    def test_flatten(self):
        self.assertEqual(
            Option.some(Option.some(6)).flatten(),
            Option.some(6),
        )
        self.assertEqual(
            Option.some(Option.none()).flatten(),
            Option.none(),
        )
        self.assertEqual(
            Option.none().flatten(),
            Option.none(),
        )
        self.assertEqual(
            Option.some(Option.some(Option.some(6))).flatten(),
            Option.some(Option.some(6)),
        )
        self.assertEqual(
            Option.some(Option.some(Option.some(6))).flatten().flatten(),
            Option.some(6),
        )


if __name__ == "__main__":
    unittest.main()
